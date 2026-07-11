# Configuración y funciones de Cloudinary para manejo de fotos
import cloudinary
import cloudinary.uploader
from app.config import settings

# ── Inicializar Cloudinary con las credenciales del .env ───
cloudinary.config(
    cloud_name  = settings.cloudinary_cloud_name,
    api_key     = settings.cloudinary_api_key,
    api_secret  = settings.cloudinary_api_secret,
    secure      = True,   # Siempre usar HTTPS
)


def subir_foto_personal(
    archivo_bytes: bytes,
    dni: str,
) -> str:
    """
    Sube la foto de un trabajador a Cloudinary.

    - Carpeta: unamba_rrhh/fotos_personal/
    - Public ID: el DNI del trabajador (para sobrescribir si ya existe)
    - Transformación: recorte centrado en cara, 400x400 px
    - Retorna: URL pública segura (HTTPS)
    """
    resultado = cloudinary.uploader.upload(
        archivo_bytes,
        folder          = "unamba_rrhh/fotos_personal",
        public_id       = f"foto_{dni}",
        overwrite       = True,        # Si ya existe, reemplazar
        resource_type   = "image",
        allowed_formats = ["jpg", "jpeg", "png", "webp"],
        transformation  = [
            {
                "width":   400,
                "height":  400,
                "crop":    "fill",
                "gravity": "face",     # Centra en la cara automáticamente
                "quality": "auto",     # Optimiza calidad automáticamente
                "fetch_format": "auto" # Convierte a WebP si el navegador lo soporta
            }
        ]
    )
    return resultado["secure_url"]


def eliminar_foto_personal(dni: str) -> bool:
    """
    Elimina la foto de un trabajador de Cloudinary.
    Útil cuando se elimina el registro completo.
    Retorna True si se eliminó correctamente.
    """
    resultado = cloudinary.uploader.destroy(
        f"unamba_rrhh/fotos_personal/foto_{dni}"
    )
    return resultado.get("result") == "ok"