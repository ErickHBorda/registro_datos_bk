# Modelos SQLAlchemy para formación, experiencia y reconocimientos
import enum
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Integer,
    SmallInteger, String, Text, Enum, ForeignKey, func,
)
from sqlalchemy.orm import relationship
from app.database import Base


# ── MODELO: formacion_academica ────────────────────────────

class NivelEducativoEnum(str, enum.Enum):
    primaria             = "Primaria"
    secundaria           = "Secundaria"
    tecnico              = "Técnico"
    bachiller            = "Bachiller Universitario"
    titulo               = "Título Universitario"
    segunda_especialidad = "Segunda Especialidad"
    maestria             = "Maestría"
    doctorado            = "Doctorado"

class EstadoEstudioEnum(str, enum.Enum):
    completo   = "Completo"
    incompleto = "Incompleto"
    en_curso   = "En curso"


class FormacionAcademica(Base):
    __tablename__ = "formacion_academica"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False)

    nivel               = Column(Enum(NivelEducativoEnum, name="nivel_educativo_tipo"), nullable=False)
    estado              = Column(Enum(EstadoEstudioEnum,  name="estado_estudio_tipo"),  nullable=False)
    centro_estudios     = Column(String(200))
    grado_obtenido      = Column(String(150))
    mencion             = Column(String(150))
    fecha_inicio        = Column(Date)
    fecha_conclusion    = Column(Date)
    documento_acredita  = Column(String(150))
    orden               = Column(SmallInteger, nullable=False, default=1)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="formacion_academica")


# ── MODELO: otros_estudios ─────────────────────────────────

class TipoOtroEstudioEnum(str, enum.Enum):
    diplomado       = "Diplomado"
    especializacion = "Especialización"
    otro            = "Otro"

class TipoConstanciaEnum(str, enum.Enum):
    certificado = "Certificado"
    diploma     = "Diploma"
    constancia  = "Constancia"
    resolucion  = "Resolución"
    otro        = "Otro"


class OtrosEstudios(Base):
    __tablename__ = "otros_estudios"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False)

    tipo                = Column(Enum(TipoOtroEstudioEnum, name="tipo_otro_estudio_tipo"), nullable=False)
    nombre_curso        = Column(String(200), nullable=False)
    centro_estudios     = Column(String(200), nullable=False)
    fecha_inicio        = Column(Date)
    fecha_fin           = Column(Date)
    fecha_emision       = Column(Date)
    duracion_horas      = Column(SmallInteger)
    tipo_constancia     = Column(Enum(TipoConstanciaEnum, name="tipo_constancia_tipo"))
    orden               = Column(SmallInteger, nullable=False, default=1)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="otros_estudios")


# ── MODELO: experiencia_laboral ────────────────────────────

class TipoInstitucionEnum(str, enum.Enum):
    estatal = "Estatal"
    privada = "Privada"


class ExperienciaLaboral(Base):
    __tablename__ = "experiencia_laboral"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False)

    tipo_institucion    = Column(Enum(TipoInstitucionEnum, name="tipo_institucion_tipo"), nullable=False)
    nombre_entidad      = Column(String(200), nullable=False)
    cargo               = Column(String(150), nullable=False)
    documento_acredita  = Column(String(150))
    fecha_inicio        = Column(Date, nullable=False)
    fecha_culminacion   = Column(Date)
    tiempo_cargo        = Column(String(50))
    orden               = Column(SmallInteger, nullable=False, default=1)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="experiencia_laboral")


# ── MODELO: experiencia_docente ────────────────────────────

class ExperienciaDocente(Base):
    __tablename__ = "experiencia_docente"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False)

    nombre_entidad      = Column(String(200), nullable=False)
    categoria           = Column(String(100))
    documento_acredita  = Column(String(150))
    fecha_inicio        = Column(Date, nullable=False)
    fecha_culminacion   = Column(Date)
    tiempo_cargo        = Column(String(50))
    orden               = Column(SmallInteger, nullable=False, default=1)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="experiencia_docente")


# ── MODELO: otras_instituciones ────────────────────────────

class OtrasInstituciones(Base):
    __tablename__ = "otras_instituciones"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False, unique=True)

    labora_otra_inst    = Column(Boolean, nullable=False, default=False)
    tipo_personal       = Column(String(20))
    nombre_entidad      = Column(String(200))

    dia_lunes           = Column(Boolean, default=False)
    dia_martes          = Column(Boolean, default=False)
    dia_miercoles       = Column(Boolean, default=False)
    dia_jueves          = Column(Boolean, default=False)
    dia_viernes         = Column(Boolean, default=False)

    horas_diarias       = Column(SmallInteger)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="otras_instituciones")


# ── MODELO: reconocimientos ────────────────────────────────

class Reconocimiento(Base):
    __tablename__ = "reconocimientos"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False)

    nombre_entidad      = Column(String(200), nullable=False)
    tipo_reconocimiento = Column(String(200), nullable=False)
    documento_acredita  = Column(String(150))
    fecha_documento     = Column(Date)
    orden               = Column(SmallInteger, nullable=False, default=1)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="reconocimientos")