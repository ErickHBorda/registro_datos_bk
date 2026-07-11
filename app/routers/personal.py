# Endpoints CRUD para el registro completo del personal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.personal import Personal, DatosLaborales, Familiar
from app.models.academico import (
    FormacionAcademica, OtrosEstudios,
    ExperienciaLaboral, ExperienciaDocente,
    OtrasInstituciones, Reconocimiento,
)
from app.schemas.personal import (
    PersonalCreate, PersonalUpdate, PersonalResponse,
    DatosLaboralesCreate, DatosLaboralesResponse,
    FamiliarCreate, FamiliarResponse,
)
from app.schemas.academico import (
    FormacionAcademicaCreate, FormacionAcademicaResponse,
    OtrosEstudiosCreate, OtrosEstudiosResponse,
    ExperienciaLaboralCreate, ExperienciaLaboralResponse,
    ExperienciaDocenteCreate, ExperienciaDocenteResponse,
    OtrasInstitucionesCreate, OtrasInstitucionesResponse,
    ReconocimientoCreate, ReconocimientoResponse,
)
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(
    prefix="/api/personal",
    tags=["Personal"],
)


# ── Schema de registro completo ────────────────────────────
# Recibe toda la ficha en una sola petición

class FichaCompletaCreate(BaseModel):
    personal:             PersonalCreate
    datos_laborales:      Optional[DatosLaboralesCreate]      = None
    familiares:           List[FamiliarCreate]                = []
    formacion_academica:  List[FormacionAcademicaCreate]      = []
    otros_estudios:       List[OtrosEstudiosCreate]           = []
    experiencia_laboral:  List[ExperienciaLaboralCreate]      = []
    experiencia_docente:  List[ExperienciaDocenteCreate]      = []
    otras_instituciones:  Optional[OtrasInstitucionesCreate]  = None
    reconocimientos:      List[ReconocimientoCreate]          = []


class FichaCompletaResponse(BaseModel):
    personal:             PersonalResponse
    datos_laborales:      Optional[DatosLaboralesResponse]    = None
    familiares:           List[FamiliarResponse]              = []
    formacion_academica:  List[FormacionAcademicaResponse]    = []
    otros_estudios:       List[OtrosEstudiosResponse]         = []
    experiencia_laboral:  List[ExperienciaLaboralResponse]    = []
    experiencia_docente:  List[ExperienciaDocenteResponse]    = []
    otras_instituciones:  Optional[OtrasInstitucionesResponse] = None
    reconocimientos:      List[ReconocimientoResponse]        = []

    model_config = {"from_attributes": True}


# ── Función auxiliar: cargar trabajador con relaciones ─────

async def obtener_personal_completo(
    personal_id: int,
    db: AsyncSession,
) -> Personal:
    """
    Carga el registro de personal con todas sus
    relaciones en una sola consulta optimizada.
    """
    resultado = await db.execute(
        select(Personal)
        .options(
            selectinload(Personal.datos_laborales),
            selectinload(Personal.familiares),
            selectinload(Personal.formacion_academica),
            selectinload(Personal.otros_estudios),
            selectinload(Personal.experiencia_laboral),
            selectinload(Personal.experiencia_docente),
            selectinload(Personal.otras_instituciones),
            selectinload(Personal.reconocimientos),
        )
        .where(Personal.id == personal_id)
    )
    return resultado.scalar_one_or_none()


# ══════════════════════════════════════════════════════════
# POST /api/personal/
# Registrar ficha completa de un nuevo trabajador
# ══════════════════════════════════════════════════════════

@router.post(
    "/",
    response_model=FichaCompletaResponse,
    status_code=201,
    summary="Registrar ficha completa de un nuevo trabajador",
)
async def crear_personal(
    ficha: FichaCompletaCreate,
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Verificar DNI duplicado ─────────────────────────
    existente = await db.execute(
        select(Personal).where(Personal.dni == ficha.personal.dni)
    )
    if existente.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un trabajador registrado con el DNI {ficha.personal.dni}"
        )

    # ── 2. Crear registro principal ────────────────────────
    datos_personal = ficha.personal.model_dump()
    # Convertir idiomas y ofimática a dict para JSONB
    datos_personal["idiomas_nativos"] = [
        i.model_dump() for i in ficha.personal.idiomas_nativos
    ]
    datos_personal["ofimatica"] = [
        o.model_dump() for o in ficha.personal.ofimatica
    ]

    nuevo_personal = Personal(**datos_personal)
    db.add(nuevo_personal)
    await db.flush()   # Obtiene el ID sin hacer commit aún

    personal_id = nuevo_personal.id

    # ── 3. Datos laborales ─────────────────────────────────
    if ficha.datos_laborales:
        db.add(DatosLaborales(
            personal_id=personal_id,
            **ficha.datos_laborales.model_dump()
        ))

    # ── 4. Familiares ──────────────────────────────────────
    for familiar in ficha.familiares:
        db.add(Familiar(
            personal_id=personal_id,
            **familiar.model_dump()
        ))

    # ── 5. Formación académica ─────────────────────────────
    for formacion in ficha.formacion_academica:
        db.add(FormacionAcademica(
            personal_id=personal_id,
            **formacion.model_dump()
        ))

    # ── 6. Otros estudios ──────────────────────────────────
    for estudio in ficha.otros_estudios:
        db.add(OtrosEstudios(
            personal_id=personal_id,
            **estudio.model_dump()
        ))

    # ── 7. Experiencia laboral ─────────────────────────────
    for exp in ficha.experiencia_laboral:
        db.add(ExperienciaLaboral(
            personal_id=personal_id,
            **exp.model_dump()
        ))

    # ── 8. Experiencia docente ─────────────────────────────
    for doc in ficha.experiencia_docente:
        db.add(ExperienciaDocente(
            personal_id=personal_id,
            **doc.model_dump()
        ))

    # ── 9. Otras instituciones ─────────────────────────────
    if ficha.otras_instituciones:
        db.add(OtrasInstituciones(
            personal_id=personal_id,
            **ficha.otras_instituciones.model_dump()
        ))

    # ── 10. Reconocimientos ────────────────────────────────
    for rec in ficha.reconocimientos:
        db.add(Reconocimiento(
            personal_id=personal_id,
            **rec.model_dump()
        ))

    # ── 11. Confirmar toda la transacción ──────────────────
    await db.commit()

    # ── 12. Recargar con todas las relaciones ──────────────
    trabajador = await obtener_personal_completo(personal_id, db)

    return {
        "personal":            trabajador,
        "datos_laborales":     trabajador.datos_laborales,
        "familiares":          trabajador.familiares,
        "formacion_academica": trabajador.formacion_academica,
        "otros_estudios":      trabajador.otros_estudios,
        "experiencia_laboral": trabajador.experiencia_laboral,
        "experiencia_docente": trabajador.experiencia_docente,
        "otras_instituciones": trabajador.otras_instituciones,
        "reconocimientos":     trabajador.reconocimientos,
    }


# ══════════════════════════════════════════════════════════
# GET /api/personal/{id}
# Obtener ficha completa de un trabajador por ID
# ══════════════════════════════════════════════════════════

@router.get(
    "/{personal_id}",
    response_model=FichaCompletaResponse,
    summary="Obtener ficha completa de un trabajador",
)
async def obtener_personal(
    personal_id: int,
    db: AsyncSession = Depends(get_db),
):
    trabajador = await obtener_personal_completo(personal_id, db)

    if not trabajador:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró un trabajador con ID {personal_id}"
        )

    return {
        "personal":            trabajador,
        "datos_laborales":     trabajador.datos_laborales,
        "familiares":          trabajador.familiares,
        "formacion_academica": trabajador.formacion_academica,
        "otros_estudios":      trabajador.otros_estudios,
        "experiencia_laboral": trabajador.experiencia_laboral,
        "experiencia_docente": trabajador.experiencia_docente,
        "otras_instituciones": trabajador.otras_instituciones,
        "reconocimientos":     trabajador.reconocimientos,
    }


# ══════════════════════════════════════════════════════════
# GET /api/personal/dni/{dni}
# Obtener ficha completa por DNI (más natural para RR.HH.)
# ══════════════════════════════════════════════════════════

@router.get(
    "/dni/{dni}",
    response_model=FichaCompletaResponse,
    summary="Obtener ficha completa de un trabajador por DNI",
)
async def obtener_personal_por_dni(
    dni: str,
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(Personal)
        .options(
            selectinload(Personal.datos_laborales),
            selectinload(Personal.familiares),
            selectinload(Personal.formacion_academica),
            selectinload(Personal.otros_estudios),
            selectinload(Personal.experiencia_laboral),
            selectinload(Personal.experiencia_docente),
            selectinload(Personal.otras_instituciones),
            selectinload(Personal.reconocimientos),
        )
        .where(Personal.dni == dni)
    )
    trabajador = resultado.scalar_one_or_none()

    if not trabajador:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró un trabajador con DNI {dni}"
        )

    return {
        "personal":            trabajador,
        "datos_laborales":     trabajador.datos_laborales,
        "familiares":          trabajador.familiares,
        "formacion_academica": trabajador.formacion_academica,
        "otros_estudios":      trabajador.otros_estudios,
        "experiencia_laboral": trabajador.experiencia_laboral,
        "experiencia_docente": trabajador.experiencia_docente,
        "otras_instituciones": trabajador.otras_instituciones,
        "reconocimientos":     trabajador.reconocimientos,
    }


# ══════════════════════════════════════════════════════════
# GET /api/personal/
# Listar todos los trabajadores (resumen, sin relaciones)
# ══════════════════════════════════════════════════════════

class PersonalResumen(BaseModel):
    id:               int
    apellido_paterno: str
    apellido_materno: str
    nombres:          str
    dni:              str
    foto_url:         Optional[str] = None
    creado_en:        datetime

    model_config = {"from_attributes": True}


@router.get(
    "/",
    response_model=List[PersonalResumen],
    summary="Listar todos los trabajadores registrados",
)
async def listar_personal(
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(
        select(Personal).order_by(
            Personal.apellido_paterno,
            Personal.apellido_materno,
        )
    )
    return resultado.scalars().all()


# ══════════════════════════════════════════════════════════
# PUT /api/personal/{id}
# Actualizar ficha completa de un trabajador
# ══════════════════════════════════════════════════════════

@router.put(
    "/{personal_id}",
    response_model=FichaCompletaResponse,
    summary="Actualizar ficha completa de un trabajador",
)
async def actualizar_personal(
    personal_id: int,
    ficha: FichaCompletaCreate,
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Verificar que existe ────────────────────────────
    trabajador = await obtener_personal_completo(personal_id, db)
    if not trabajador:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró un trabajador con ID {personal_id}"
        )

    # ── 2. Verificar DNI duplicado (si cambió) ─────────────
    if ficha.personal.dni != trabajador.dni:
        duplicado = await db.execute(
            select(Personal).where(
                Personal.dni == ficha.personal.dni,
                Personal.id  != personal_id,
            )
        )
        if duplicado.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"El DNI {ficha.personal.dni} ya pertenece a otro trabajador"
            )

    # ── 3. Actualizar datos personales ─────────────────────
    datos_personal = ficha.personal.model_dump()
    datos_personal["idiomas_nativos"] = [
        i.model_dump() for i in ficha.personal.idiomas_nativos
    ]
    datos_personal["ofimatica"] = [
        o.model_dump() for o in ficha.personal.ofimatica
    ]

    for campo, valor in datos_personal.items():
        setattr(trabajador, campo, valor)

    # ── 4. Actualizar datos laborales ──────────────────────
    if ficha.datos_laborales:
        if trabajador.datos_laborales:
            for campo, valor in ficha.datos_laborales.model_dump().items():
                setattr(trabajador.datos_laborales, campo, valor)
        else:
            db.add(DatosLaborales(
                personal_id=personal_id,
                **ficha.datos_laborales.model_dump()
            ))

    # ── 5. Reemplazar listas (eliminar y volver a insertar) ─
    # Familiares
    for f in trabajador.familiares:
        await db.delete(f)
    for familiar in ficha.familiares:
        db.add(Familiar(personal_id=personal_id, **familiar.model_dump()))

    # Formación académica
    for f in trabajador.formacion_academica:
        await db.delete(f)
    for formacion in ficha.formacion_academica:
        db.add(FormacionAcademica(personal_id=personal_id, **formacion.model_dump()))

    # Otros estudios
    for e in trabajador.otros_estudios:
        await db.delete(e)
    for estudio in ficha.otros_estudios:
        db.add(OtrosEstudios(personal_id=personal_id, **estudio.model_dump()))

    # Experiencia laboral
    for e in trabajador.experiencia_laboral:
        await db.delete(e)
    for exp in ficha.experiencia_laboral:
        db.add(ExperienciaLaboral(personal_id=personal_id, **exp.model_dump()))

    # Experiencia docente
    for e in trabajador.experiencia_docente:
        await db.delete(e)
    for doc in ficha.experiencia_docente:
        db.add(ExperienciaDocente(personal_id=personal_id, **doc.model_dump()))

    # Otras instituciones
    if trabajador.otras_instituciones:
        await db.delete(trabajador.otras_instituciones)
    if ficha.otras_instituciones:
        db.add(OtrasInstituciones(
            personal_id=personal_id,
            **ficha.otras_instituciones.model_dump()
        ))

    # Reconocimientos
    for r in trabajador.reconocimientos:
        await db.delete(r)
    for rec in ficha.reconocimientos:
        db.add(Reconocimiento(personal_id=personal_id, **rec.model_dump()))

    # ── 6. Confirmar cambios ───────────────────────────────
    await db.commit()

    # ── 7. Recargar y devolver ─────────────────────────────
    trabajador_actualizado = await obtener_personal_completo(personal_id, db)
    return {
        "personal":            trabajador_actualizado,
        "datos_laborales":     trabajador_actualizado.datos_laborales,
        "familiares":          trabajador_actualizado.familiares,
        "formacion_academica": trabajador_actualizado.formacion_academica,
        "otros_estudios":      trabajador_actualizado.otros_estudios,
        "experiencia_laboral": trabajador_actualizado.experiencia_laboral,
        "experiencia_docente": trabajador_actualizado.experiencia_docente,
        "otras_instituciones": trabajador_actualizado.otras_instituciones,
        "reconocimientos":     trabajador_actualizado.reconocimientos,
    }