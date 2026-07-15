# Autenticación JWT para el panel de administración
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from jose import jwt
from app.config import settings

# ── Configuración ──────────────────────────────────────────
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# ── Schemas ────────────────────────────────────────────────
class LoginRequest(BaseModel):
    usuario: str
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nombre: str


# ── Endpoints ──────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(datos: LoginRequest):
    if (
        datos.usuario != settings.admin_usuario
        or datos.contrasena != settings.admin_contrasena
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    payload = {
        "sub": datos.usuario,
        "exp": datetime.utcnow() + timedelta(hours=settings.admin_token_hours),
        "role": "admin",
    }
    token = jwt.encode(payload, settings.admin_secret_key, algorithm=ALGORITHM)
    return TokenResponse(
        access_token=token,
        nombre="Escalafón — UNAMBA",
    )
