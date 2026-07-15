from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Base de datos
    database_url: str

    # Cloudinary
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    # App
    app_name: str = "Ficha Digital UNAMBA 2025"
    app_version: str = "1.0.0"
    debug: bool = True

    # Admin — credenciales y JWT
    admin_usuario: str
    admin_contrasena: str
    admin_secret_key: str
    admin_token_hours: int = 8

    # CORS — acepta formato JSON ["url1","url2"] desde el .env
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Permite leer listas con formato ["a","b"] desde el .env
        env_parse_default_factory = True


# Instancia única reutilizable en toda la app
settings = Settings()
