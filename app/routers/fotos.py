# Endpoint para subir y actualizar la foto de perfil del personal
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models.personal import Personal
from app.cloudinary_config import subir_foto_personal, eliminar_foto_personal

router = APIRouter(
    prefix="/api/fotos",
    tags=["Fotos de Personal"],
)

# ── Tipos y tamaño permitidos ──────────────────────────────
TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
TAMANO_MAXIMO_MB = 5
TAMANO_MAXIMO_BYTES = TAMANO_MAXIMO_MB * 1024 * 1024


@router.post(
    "/{personal_id}",
    summary="Subir o actualizar foto de perfil",
    response_model=dict,
)
async def subir_foto(
    personal_id: int,
    archivo: UploadFile = File(..., description="Foto en JPG, PNG o WebP. Máx. 5MB"),
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Verificar que el trabajador existe ──────────────
    resultado = await db.execute(
        select(Personal).where(Personal.id == personal_id)
    )
    trabajador = resultado.scalar_one_or_none()

    if not trabajador:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró un trabajador con ID {personal_id}"
        )

    # ── 2. Validar tipo de archivo ─────────────────────────
    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tipo de archivo no permitido: {archivo.content_type}. "
                f"Solo se aceptan: JPG, PNG o WebP"
            )
        )

    # ── 3. Validar tamaño ─────────────────────────────────
    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo supera el tamaño máximo permitido de {TAMANO_MAXIMO_MB}MB"
        )

    # ── 4. Subir a Cloudinary ──────────────────────────────
    try:
        url_foto = subir_foto_personal(
            archivo_bytes = contenido,
            dni           = trabajador.dni,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir la foto a Cloudinary: {str(e)}"
        )

    # ── 5. Guardar URL en la base de datos ─────────────────
    await db.execute(
        update(Personal)
        .where(Personal.id == personal_id)
        .values(foto_url=url_foto)
    )
    await db.commit()

    return {
        "mensaje": "Foto actualizada correctamente",
        "personal_id": personal_id,
        "foto_url": url_foto,
    }


@router.delete(
    "/{personal_id}",
    summary="Eliminar foto de perfil",
    response_model=dict,
)
async def eliminar_foto(
    personal_id: int,
    db: AsyncSession = Depends(get_db),
):
    # ── 1. Verificar que el trabajador existe ──────────────
    resultado = await db.execute(
        select(Personal).where(Personal.id == personal_id)
    )
    trabajador = resultado.scalar_one_or_none()

    if not trabajador:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró un trabajador con ID {personal_id}"
        )

    if not trabajador.foto_url:
        raise HTTPException(
            status_code=404,
            detail="Este trabajador no tiene foto registrada"
        )

    # ── 2. Eliminar de Cloudinary ──────────────────────────
    try:
        eliminar_foto_personal(dni=trabajador.dni)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar la foto de Cloudinary: {str(e)}"
        )

    # ── 3. Limpiar URL en la base de datos ─────────────────
    await db.execute(
        update(Personal)
        .where(Personal.id == personal_id)
        .values(foto_url=None)
    )
    await db.commit()

    return {
        "mensaje": "Foto eliminada correctamente",
        "personal_id": personal_id,
    }