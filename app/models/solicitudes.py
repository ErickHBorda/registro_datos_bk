# Modelo SQLAlchemy para solicitudes de actualización
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class SolicitudActualizacion(Base):
    __tablename__ = "solicitudes_actualizacion"

    id = Column(Integer, primary_key=True, index=True)
    personal_id = Column(
        Integer,
        ForeignKey("personal.id", ondelete="CASCADE"),
        nullable=False,
    )
    estado = Column(String(20), default="pendiente", nullable=False)
    motivo = Column(Text, nullable=True)
    creado_en = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    resuelto_en = Column(DateTime(timezone=True), nullable=True)

    # Relación con personal
    personal = relationship("Personal", backref="solicitudes")
