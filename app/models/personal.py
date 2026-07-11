# Modelos SQLAlchemy para las tablas principales de la ficha
import enum
from datetime import date, datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Integer,
    SmallInteger, String, Text, Enum, ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


# ── ENUMs Python (deben coincidir con los ENUMs de PostgreSQL) ──

class SexoEnum(str, enum.Enum):
    masculino = "Masculino"
    femenino  = "Femenino"

class EstadoCivilEnum(str, enum.Enum):
    soltero    = "Soltero"
    casado     = "Casada"
    viudo      = "Viudo"
    divorciado = "Divorciado"
    otro       = "Otro"

class TipoViviendaEnum(str, enum.Enum):
    propia      = "Propia"
    alquilada   = "Alquilada"
    departamento = "Departamento"
    quinta      = "Quinta"
    otro        = "Otro"

class SistemaPensionEnum(str, enum.Enum):
    onp = "ONP"
    afp = "AFP"

class AfpEnum(str, enum.Enum):
    integra   = "Integra"
    profuturo = "Profuturo"
    habitat   = "Habitat"
    prima     = "Prima"

class RamaMilitarEnum(str, enum.Enum):
    ejercito         = "Ejército"
    marina           = "Marina"
    aviacion         = "Aviación"
    fuerzas_especiales = "Fuerzas Especiales"


# ── MODELO: personal ───────────────────────────────────────

class Personal(Base):
    __tablename__ = "personal"

    id                   = Column(Integer, primary_key=True, index=True)
    foto_url             = Column(Text)

    # Nombres
    apellido_paterno     = Column(String(60),  nullable=False)
    apellido_materno     = Column(String(60),  nullable=False)
    nombres              = Column(String(100), nullable=False)

    # Documento
    dni                  = Column(String(8),   nullable=False, unique=True)
    libreta_militar      = Column(String(20))

    # Datos demográficos
    sexo                 = Column(Enum(SexoEnum,       name="sexo_tipo"),        nullable=False)
    fecha_nacimiento     = Column(Date,                                           nullable=False)
    estado_civil         = Column(Enum(EstadoCivilEnum, name="estado_civil_tipo"), nullable=False)

    # Lugar de nacimiento
    nac_pais             = Column(String(60),  nullable=False, default="Perú")
    nac_departamento     = Column(String(60),  nullable=False)
    nac_provincia        = Column(String(60),  nullable=False)
    nac_distrito         = Column(String(60),  nullable=False)

    # Contacto
    telefono_fijo        = Column(String(15))
    celular              = Column(String(15),  nullable=False)
    email_personal_1     = Column(String(100), nullable=False)
    email_personal_2     = Column(String(100))

    # Domicilio
    dom_tipo_via         = Column(String(20))
    dom_direccion        = Column(String(200), nullable=False)
    dom_referencia       = Column(String(200))
    tipo_vivienda        = Column(Enum(TipoViviendaEnum, name="tipo_vivienda_tipo"))

    # Datos complementarios
    ruc                  = Column(String(11))
    licencia_conducir    = Column(String(20))
    afiliacion_essalud   = Column(String(30))
    grupo_sanguineo      = Column(String(5))
    donador_organos      = Column(Boolean, default=False)

    # Cuenta bancaria
    banco                = Column(String(60))
    cuenta_numero        = Column(String(30))
    cuenta_cci           = Column(String(30))

    # Denominación profesional
    denominacion_prof    = Column(String(100))
    abreviatura_prof     = Column(String(20))

    # Colegio profesional
    colegio_prof_nombre  = Column(String(100))
    colegio_prof_numero  = Column(String(30))
    colegio_prof_fecha   = Column(Date)

    # Pensiones
    sistema_pension      = Column(Enum(SistemaPensionEnum, name="sistema_pension_tipo"))
    afp_nombre           = Column(Enum(AfpEnum,            name="afp_tipo"))

    # Discapacidad
    tiene_discapacidad   = Column(Boolean, default=False)
    conadis_registro     = Column(String(30))

    # Servicio militar
    realizo_serv_militar      = Column(Boolean, default=False)
    serv_militar_rama         = Column(Enum(RamaMilitarEnum, name="rama_militar_tipo"))
    serv_militar_cargo        = Column(String(100))
    serv_militar_fecha_inicio = Column(Date)
    serv_militar_fecha_fin    = Column(Date)

    # JSONB
    idiomas_nativos      = Column(JSONB, default=list)
    ofimatica            = Column(JSONB, default=list)

    # Auditoría
    creado_en            = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ── Relaciones ─────────────────────────────────────────
    datos_laborales      = relationship("DatosLaborales",    back_populates="personal", uselist=False, cascade="all, delete-orphan")
    familiares           = relationship("Familiar",          back_populates="personal", cascade="all, delete-orphan")
    formacion_academica  = relationship("FormacionAcademica",back_populates="personal", cascade="all, delete-orphan")
    otros_estudios       = relationship("OtrosEstudios",     back_populates="personal", cascade="all, delete-orphan")
    experiencia_laboral  = relationship("ExperienciaLaboral",back_populates="personal", cascade="all, delete-orphan")
    experiencia_docente  = relationship("ExperienciaDocente",back_populates="personal", cascade="all, delete-orphan")
    otras_instituciones  = relationship("OtrasInstituciones",back_populates="personal", uselist=False, cascade="all, delete-orphan")
    reconocimientos      = relationship("Reconocimiento",    back_populates="personal", cascade="all, delete-orphan")


# ── MODELO: datos_laborales ────────────────────────────────

class CondicionEnum(str, enum.Enum):
    nombrado   = "Nombrado"
    contratado = "Contratado"

class TipoPersonalEnum(str, enum.Enum):
    docente        = "Docente"
    administrativo = "Administrativo"

class Regimen276Enum(str, enum.Enum):
    ordinario   = "Ordinario"
    profesional = "Profesional"
    tecnico     = "Técnico"
    auxiliar    = "Auxiliar"
    principal   = "Principal"
    asociado    = "Asociado"
    jp          = "JP"

class Regimen1057Enum(str, enum.Enum):
    cas_permanente  = "CAS Permanente"
    cas_determinado = "CAS Determinado"
    cas_confianza   = "CAS Confianza"
    dc_a1 = "DC-A1"
    dc_a2 = "DC-A2"
    dc_a3 = "DC-A3"
    dc_b1 = "DC-B1"
    dc_b2 = "DC-B2"

class NivelRemunerativoEnum(str, enum.Enum):
    a = "A"
    b = "B"
    c = "C"
    d = "D"
    e = "E"
    f = "F"

class DedicacionEnum(str, enum.Enum):
    de    = "DE"
    tc    = "TC"
    tp    = "TP"
    horas = "Horas"


class DatosLaborales(Base):
    __tablename__ = "datos_laborales"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False, unique=True)

    dependencia         = Column(String(150), nullable=False)
    cargo               = Column(String(150), nullable=False)
    fecha_ingreso       = Column(Date,        nullable=False)
    email_institucional = Column(String(100), nullable=False)

    condicion           = Column(Enum(CondicionEnum,          name="condicion_tipo"),          nullable=False)
    tipo_personal       = Column(Enum(TipoPersonalEnum,       name="tipo_personal_tipo"),      nullable=False)
    regimen_276         = Column(Enum(Regimen276Enum,         name="regimen_276_tipo"))
    regimen_1057        = Column(Enum(Regimen1057Enum,        name="regimen_1057_tipo"))
    regimen_otros       = Column(String(100))
    nivel_remunerativo  = Column(Enum(NivelRemunerativoEnum,  name="nivel_remunerativo_tipo"))
    dedicacion          = Column(Enum(DedicacionEnum,         name="dedicacion_tipo"))
    horas_semanales     = Column(SmallInteger)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="datos_laborales")


# ── MODELO: familiares ─────────────────────────────────────

class ParentescoEnum(str, enum.Enum):
    conyuge = "Cónyuge"
    hijo    = "Hijo"
    hija    = "Hija"
    padre   = "Padre"
    madre   = "Madre"


class Familiar(Base):
    __tablename__ = "familiares"

    id                  = Column(Integer, primary_key=True, index=True)
    personal_id         = Column(Integer, ForeignKey("personal.id", ondelete="CASCADE"), nullable=False)

    apellido_paterno    = Column(String(60),  nullable=False)
    apellido_materno    = Column(String(60),  nullable=False)
    nombres             = Column(String(100), nullable=False)
    parentesco          = Column(Enum(ParentescoEnum, name="parentesco_tipo"), nullable=False)
    dni                 = Column(String(8))
    fecha_nacimiento    = Column(Date)
    sexo                = Column(Enum(SexoEnum, name="sexo_tipo"))

    nac_pais            = Column(String(60), default="Perú")
    nac_departamento    = Column(String(60))
    nac_provincia       = Column(String(60))
    nac_distrito        = Column(String(60))
    nac_anexo           = Column(String(60))

    vive_con_trabajador = Column(Boolean, default=False)

    creado_en           = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    personal            = relationship("Personal", back_populates="familiares")