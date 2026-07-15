# Schemas Pydantic para solicitudes de actualización
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SolicitudCreate(BaseModel):
    personal_id: int
    motivo: Optional[str] = None


class SolicitudResponse(BaseModel):
    id: int
    personal_id: int
    estado: str
    motivo: Optional[str] = None
    creado_en: datetime
    resuelto_en: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SolicitudConPersonal(SolicitudResponse):
    """Respuesta enriquecida con datos del trabajador"""

    apellido_paterno: str
    apellido_materno: str
    nombres: str
    dni: str
    foto_url: Optional[str] = None
    cargo: Optional[str] = None
    dependencia: Optional[str] = None


class ResolverSolicitud(BaseModel):
    estado: str  # "aprobada" | "rechazada"
    motivo: Optional[str] = None
