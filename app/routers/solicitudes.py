# Endpoints para solicitudes de actualización de ficha
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy import case

from app.database import get_db
from app.dependencies import verificar_token
from app.models.solicitudes import SolicitudActualizacion
from app.models.personal import Personal, DatosLaborales
from app.schemas.solicitudes import (
    SolicitudCreate,
    SolicitudResponse,
    SolicitudConPersonal,
    ResolverSolicitud,
)

# ── Router público (trabajador) ────────────────────────────
router_publico = APIRouter(
    prefix="/solicitudes",
    tags=["Solicitudes"],
)

# ── Router admin (encargada) ───────────────────────────────
router_admin = APIRouter(
    prefix="/admin/solicitudes",
    tags=["Admin — Solicitudes"],
    dependencies=[Depends(verificar_token)],
)


# ══ ENDPOINTS PÚBLICOS ═════════════════════════════════════


# POST /solicitudes — crear solicitud de actualización
@router_publico.post("", response_model=SolicitudResponse)
async def crear_solicitud(
    datos: SolicitudCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verificar que el personal existe
    p = await db.get(Personal, datos.personal_id)
    if not p:
        raise HTTPException(
            status_code=404,
            detail="Trabajador no encontrado",
        )

    # Verificar si ya tiene una solicitud pendiente
    q = await db.execute(
        select(SolicitudActualizacion).where(
            SolicitudActualizacion.personal_id == datos.personal_id,
            SolicitudActualizacion.estado == "pendiente",
        )
    )
    existente = q.scalar_one_or_none()
    if existente:
        raise HTTPException(
            status_code=409,
            detail="Ya tienes una solicitud pendiente de revisión",
        )

    solicitud = SolicitudActualizacion(
        personal_id=datos.personal_id,
        motivo=datos.motivo,
    )
    db.add(solicitud)
    await db.commit()
    await db.refresh(solicitud)
    return solicitud


# GET /solicitudes/estado/{dni} — consultar estado por DNI
@router_publico.get("/estado/{dni}")
async def estado_solicitud(
    dni: str,
    db: AsyncSession = Depends(get_db),
):
    # Buscar personal por DNI
    q = await db.execute(select(Personal).where(Personal.dni == dni))
    p = q.scalar_one_or_none()
    if not p:
        return {"existe": False}

    # Buscar solicitud más reciente
    # Buscar solicitud por prioridad: aprobada > pendiente > rechazada
    q = await db.execute(
        select(SolicitudActualizacion)
        .where(
            SolicitudActualizacion.personal_id == p.id,
            SolicitudActualizacion.estado != "resuelta",
        )
        .order_by(
            case(
                (SolicitudActualizacion.estado == "aprobada", 0),
                (SolicitudActualizacion.estado == "pendiente", 1),
                (SolicitudActualizacion.estado == "rechazada", 2),
                else_=3,
            ),
            SolicitudActualizacion.creado_en.desc(),
        )
        .limit(1)
    )
    solicitud = q.scalar_one_or_none()

    return {
        "existe": True,
        "personal_id": p.id,
        "nombre": f"{p.apellido_paterno} {p.apellido_materno}, {p.nombres}",
        "foto_url": p.foto_url,
        "solicitud": (
            {
                "id": solicitud.id if solicitud else None,
                "estado": solicitud.estado if solicitud else None,
            }
            if solicitud
            else None
        ),
        "puede_editar": (
            solicitud and solicitud.estado == "aprobada" if solicitud else False
        ),
    }


# ══ ENDPOINTS ADMIN ════════════════════════════════════════


# GET /admin/solicitudes — listar todas las solicitudes
@router_admin.get("", response_model=List[SolicitudConPersonal])
async def listar_solicitudes(
    estado: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(SolicitudActualizacion)
        .options(
            selectinload(SolicitudActualizacion.personal).selectinload(
                Personal.datos_laborales
            )
        )
        .order_by(SolicitudActualizacion.creado_en.desc())
    )
    if estado:
        q = q.where(SolicitudActualizacion.estado == estado)

    resultado = await db.execute(q)
    solicitudes = resultado.scalars().all()

    return [
        SolicitudConPersonal(
            id=s.id,
            personal_id=s.personal_id,
            estado=s.estado,
            motivo=s.motivo,
            creado_en=s.creado_en,
            resuelto_en=s.resuelto_en,
            apellido_paterno=s.personal.apellido_paterno,
            apellido_materno=s.personal.apellido_materno,
            nombres=s.personal.nombres,
            dni=s.personal.dni,
            foto_url=s.personal.foto_url,
            cargo=(
                s.personal.datos_laborales.cargo if s.personal.datos_laborales else None
            ),
            dependencia=(
                s.personal.datos_laborales.dependencia
                if s.personal.datos_laborales
                else None
            ),
        )
        for s in solicitudes
    ]


# PUT /admin/solicitudes/{id} — aprobar o rechazar
@router_admin.put("/{solicitud_id}", response_model=SolicitudResponse)
async def resolver_solicitud(
    solicitud_id: int,
    datos: ResolverSolicitud,
    db: AsyncSession = Depends(get_db),
):
    if datos.estado not in ("aprobada", "rechazada"):
        raise HTTPException(
            status_code=400,
            detail="Estado debe ser 'aprobada' o 'rechazada'",
        )

    solicitud = await db.get(SolicitudActualizacion, solicitud_id)
    if not solicitud:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada",
        )
    if solicitud.estado != "pendiente":
        raise HTTPException(
            status_code=409,
            detail=f"La solicitud ya fue {solicitud.estado}",
        )

    solicitud.estado = datos.estado
    solicitud.resuelto_en = datetime.utcnow()
    if datos.motivo:
        solicitud.motivo = datos.motivo

    # Si se aprueba, limpiar todas las solicitudes rechazadas anteriores
    # para que no interfieran con consultas futuras
    if datos.estado == "aprobada":
        await db.execute(
            update(SolicitudActualizacion)
            .where(
                SolicitudActualizacion.personal_id == solicitud.personal_id,
                SolicitudActualizacion.id != solicitud.id,
                SolicitudActualizacion.estado == "rechazada",
            )
            .values(estado="resuelta", resuelto_en=datetime.utcnow())
        )

    await db.commit()
    await db.refresh(solicitud)
    return solicitud


# GET /admin/solicitudes/conteo — conteo por estado (para badge)
@router_admin.get("/conteo")
async def conteo_solicitudes(
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import func as sqlfunc

    q = await db.execute(
        select(
            SolicitudActualizacion.estado,
            sqlfunc.count(SolicitudActualizacion.id).label("total"),
        ).group_by(SolicitudActualizacion.estado)
    )
    resultado = q.all()
    return {r.estado: r.total for r in resultado}


# POST /solicitudes/cerrar/{personal_id}
# Cierra la solicitud aprobada una vez que el trabajador actualizó sus datos
@router_publico.post("/cerrar/{personal_id}")
async def cerrar_solicitud(
    personal_id: int,
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(
        select(SolicitudActualizacion).where(
            SolicitudActualizacion.personal_id == personal_id,
            SolicitudActualizacion.estado == "aprobada",
        )
    )
    solicitud = q.scalar_one_or_none()
    if solicitud:
        solicitud.estado = "resuelta"
        solicitud.resuelto_en = datetime.utcnow()
        await db.commit()
    return {"ok": True}
