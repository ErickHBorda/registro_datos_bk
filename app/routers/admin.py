# Endpoints del panel de administración (protegidos con JWT)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.dependencies import verificar_token
from app.models.personal import Personal, DatosLaborales
from app.routers.personal import (
    obtener_personal_completo,
    FichaCompletaResponse,
)

router = APIRouter(
    prefix="/admin",
    tags=["Administración"],
    dependencies=[Depends(verificar_token)],
)


# ── Schema resumen para la lista ───────────────────────────
class PersonalResumen(BaseModel):
    id: int
    apellido_paterno: str
    apellido_materno: str
    nombres: str
    dni: str
    foto_url: Optional[str] = None
    condicion: Optional[str] = None
    tipo_personal: Optional[str] = None
    dependencia: Optional[str] = None
    cargo: Optional[str] = None
    creado_en: str

    model_config = {"from_attributes": True}


# ── GET /admin/personal — lista con búsqueda y filtros ─────
@router.get("/personal", response_model=List[PersonalResumen])
async def listar_personal(
    busqueda: Optional[str] = None,
    tipo_personal: Optional[str] = None,
    condicion: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Personal)
        .outerjoin(Personal.datos_laborales)
        .options(selectinload(Personal.datos_laborales))
        .order_by(Personal.apellido_paterno)
    )

    # Filtro de búsqueda por nombre o DNI
    if busqueda:
        termino = f"%{busqueda}%"
        query = query.where(
            or_(
                Personal.apellido_paterno.ilike(termino),
                Personal.apellido_materno.ilike(termino),
                Personal.nombres.ilike(termino),
                Personal.dni.ilike(termino),
            )
        )

    # Filtros adicionales en datos_laborales
    if tipo_personal:
        query = query.where(DatosLaborales.tipo_personal == tipo_personal)
    if condicion:
        query = query.where(DatosLaborales.condicion == condicion)

    resultado = await db.execute(query)
    registros = resultado.scalars().unique().all()

    return [
        PersonalResumen(
            id=r.id,
            apellido_paterno=r.apellido_paterno,
            apellido_materno=r.apellido_materno,
            nombres=r.nombres,
            dni=r.dni,
            foto_url=r.foto_url,
            condicion=r.datos_laborales.condicion if r.datos_laborales else None,
            tipo_personal=(
                r.datos_laborales.tipo_personal if r.datos_laborales else None
            ),
            dependencia=r.datos_laborales.dependencia if r.datos_laborales else None,
            cargo=r.datos_laborales.cargo if r.datos_laborales else None,
            creado_en=r.creado_en.strftime("%d/%m/%Y %H:%M"),
        )
        for r in registros
    ]


# ── GET /admin/personal/{id} — ficha completa ──────────────
@router.get("/personal/{personal_id}", response_model=FichaCompletaResponse)
async def obtener_ficha(
    personal_id: int,
    db: AsyncSession = Depends(get_db),
):
    p = await obtener_personal_completo(personal_id, db)
    if not p:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    return {
        "personal": p,
        "datos_laborales": p.datos_laborales,
        "familiares": p.familiares,
        "formacion_academica": p.formacion_academica,
        "otros_estudios": p.otros_estudios,
        "experiencia_laboral": p.experiencia_laboral,
        "experiencia_docente": p.experiencia_docente,
        "otras_instituciones": p.otras_instituciones,
        "reconocimientos": p.reconocimientos,
    }


# ── DELETE /admin/personal/{id} — eliminar registro ────────
@router.delete("/personal/{personal_id}")
async def eliminar_personal(
    personal_id: int,
    db: AsyncSession = Depends(get_db),
):
    p = await db.get(Personal, personal_id)
    if not p:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    await db.delete(p)
    await db.commit()
    return {"mensaje": f"Registro {personal_id} eliminado correctamente"}
