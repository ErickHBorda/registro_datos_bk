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
TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
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
    resultado = await db.execute(select(Personal).where(Personal.id == personal_id))
    trabajador = resultado.scalar_one_or_none()
    if not trabajador:
        raise HTTPException(
            status_code=404, detail=f"No se encontró un trabajador con ID {personal_id}"
        )

    # ── 2. Leer contenido ──────────────────────────────────
    contenido = await archivo.read()

    # ── 3. Validar tamaño ─────────────────────────────────
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo supera el tamaño máximo de {TAMANO_MAXIMO_MB}MB",
        )

    # ── 4. Detectar formato real por magic bytes ───────────
    def detectar_formato(datos: bytes) -> str:
        if datos[:2] == b"\xff\xd8":
            return "image/jpeg"
        if datos[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        if b"WEBP" in datos[:12]:
            return "image/webp"
        return "desconocido"

    formato_real = detectar_formato(contenido)
    print(
        f"DEBUG formato_real={formato_real} content_type={archivo.content_type} filename={archivo.filename} primeros_bytes={contenido[:12].hex()}"
    )
    if formato_real not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Formato no permitido ({formato_real}). "
                f"Solo se aceptan: JPG, PNG o WebP."
            ),
        )

    # ── 5. Subir a Cloudinary ──────────────────────────────
    try:
        url_foto = subir_foto_personal(
            archivo_bytes=contenido,
            dni=trabajador.dni,
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error al subir la foto a Cloudinary: {str(e)}"
        )

    # ── 6. Guardar URL en la base de datos ─────────────────
    await db.execute(
        update(Personal).where(Personal.id == personal_id).values(foto_url=url_foto)
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
    resultado = await db.execute(select(Personal).where(Personal.id == personal_id))
    trabajador = resultado.scalar_one_or_none()

    if not trabajador:
        raise HTTPException(
            status_code=404, detail=f"No se encontró un trabajador con ID {personal_id}"
        )

    if not trabajador.foto_url:
        raise HTTPException(
            status_code=404, detail="Este trabajador no tiene foto registrada"
        )

    # ── 2. Eliminar de Cloudinary ──────────────────────────
    try:
        eliminar_foto_personal(dni=trabajador.dni)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar la foto de Cloudinary: {str(e)}"
        )

    # ── 3. Limpiar URL en la base de datos ─────────────────
    await db.execute(
        update(Personal).where(Personal.id == personal_id).values(foto_url=None)
    )
    await db.commit()

    return {
        "mensaje": "Foto eliminada correctamente",
        "personal_id": personal_id,
    }
