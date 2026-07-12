# Schemas Pydantic para validación de datos de entrada y salida
import re
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.models.personal import (
    SexoEnum, EstadoCivilEnum, TipoViviendaEnum,
    SistemaPensionEnum, AfpEnum, RamaMilitarEnum,
    CondicionEnum, TipoPersonalEnum,
    CategoriaRegimenEnum, RegimenDL276Enum, RegimenCASEnum,
    RegimenOrdinarioEnum, RegimenContratadoEnum,
    NivelRemunerativoEnum, DedicacionEnum,
    ParentescoEnum, NivelRenacytEnum,
)


# ── Schemas de idiomas y ofimática (JSONB) ─────────────────

class IdiomaSchema(BaseModel):
    idioma: str
    nivel: str  # Básico, Intermedio, Avanzado

    @field_validator("nivel")
    @classmethod
    def validar_nivel(cls, v):
        opciones = ["Básico", "Intermedio", "Avanzado"]
        if v not in opciones:
            raise ValueError(f"Nivel debe ser uno de: {opciones}")
        return v


class OfimaticaSchema(BaseModel):
    programa: str
    nivel: str

    @field_validator("nivel")
    @classmethod
    def validar_nivel(cls, v):
        opciones = ["Básico", "Intermedio", "Avanzado"]
        if v not in opciones:
            raise ValueError(f"Nivel debe ser uno de: {opciones}")
        return v


# ── Schema: Personal ───────────────────────────────────────

class PersonalBase(BaseModel):
    # Nombres
    apellido_paterno:   str
    apellido_materno:   str
    nombres:            str

    # Documento
    dni:                str
    libreta_militar:    Optional[str] = None

    # Datos demográficos
    sexo:               SexoEnum
    fecha_nacimiento:   date
    estado_civil:       EstadoCivilEnum

    # Lugar de nacimiento
    nac_pais:           str = "Perú"
    nac_departamento:   str
    nac_provincia:      str
    nac_distrito:       str

    # Contacto
    telefono_fijo:      Optional[str] = None
    celular:            str
    email_personal_1:   EmailStr
    email_personal_2:   Optional[EmailStr] = None

    # Domicilio
    dom_tipo_via:       Optional[str] = None
    dom_direccion:      str
    dom_referencia:     Optional[str] = None
    tipo_vivienda:      Optional[TipoViviendaEnum] = None

    # Datos complementarios
    ruc:                Optional[str] = None
    licencia_conducir:  Optional[str] = None
    afiliacion_essalud: Optional[str] = None
    grupo_sanguineo:    Optional[str] = None
    donador_organos:    bool = False

    # Cuenta bancaria
    banco:              Optional[str] = None
    cuenta_numero:      Optional[str] = None
    cuenta_cci:         Optional[str] = None

    # Denominación profesional
    denominacion_prof:  Optional[str] = None
    abreviatura_prof:   Optional[str] = None

    # Colegio profesional
    colegio_prof_nombre: Optional[str] = None
    colegio_prof_numero: Optional[str] = None
    colegio_prof_fecha:  Optional[date] = None

    # Pensiones
    sistema_pension:    Optional[SistemaPensionEnum] = None
    afp_nombre:         Optional[AfpEnum] = None

    # Discapacidad
    tiene_discapacidad: bool = False
    conadis_registro:   Optional[str] = None

    # Servicio militar
    realizo_serv_militar:      bool = False
    serv_militar_rama:         Optional[RamaMilitarEnum] = None
    serv_militar_cargo:        Optional[str] = None
    serv_militar_fecha_inicio: Optional[date] = None
    serv_militar_fecha_fin:    Optional[date] = None

    # JSONB
    idiomas_nativos:    List[IdiomaSchema]   = []
    ofimatica:          List[OfimaticaSchema] = []

    # ── Validadores ────────────────────────────────────────
    @field_validator("dni")
    @classmethod
    def validar_dni(cls, v):
        if not re.match(r"^\d{8}$", v):
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos")
        return v

    @field_validator("ruc")
    @classmethod
    def validar_ruc(cls, v):
        if v is not None and not re.match(r"^\d{11}$", v):
            raise ValueError("El RUC debe tener exactamente 11 dígitos numéricos")
        return v

    @field_validator("celular")
    @classmethod
    def validar_celular(cls, v):
        if not re.match(r"^\d{9}$", v):
            raise ValueError("El celular debe tener exactamente 9 dígitos")
        return v

    @field_validator("grupo_sanguineo")
    @classmethod
    def validar_grupo_sanguineo(cls, v):
        opciones = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if v is not None and v not in opciones:
            raise ValueError(f"Grupo sanguíneo debe ser uno de: {opciones}")
        return v

    @field_validator("idiomas_nativos")
    @classmethod
    def validar_max_idiomas(cls, v):
        if len(v) > 3:
            raise ValueError("Se permiten máximo 3 idiomas nativos")
        return v

    @field_validator("ofimatica")
    @classmethod
    def validar_max_ofimatica(cls, v):
        if len(v) > 3:
            raise ValueError("Se permiten máximo 3 programas de ofimática")
        return v

    @model_validator(mode="after")
    def validar_pension_afp(self):
        if self.sistema_pension == SistemaPensionEnum.afp and not self.afp_nombre:
            raise ValueError("Debe especificar la AFP cuando el sistema es privado")
        if self.sistema_pension == SistemaPensionEnum.onp and self.afp_nombre:
            raise ValueError("No debe especificar AFP cuando el sistema es ONP")
        return self

    @model_validator(mode="after")
    def validar_fechas_militar(self):
        if (self.serv_militar_fecha_inicio and self.serv_militar_fecha_fin):
            if self.serv_militar_fecha_fin < self.serv_militar_fecha_inicio:
                raise ValueError(
                    "La fecha de fin del servicio militar no puede ser "
                    "anterior a la fecha de inicio"
                )
        return self


class PersonalCreate(PersonalBase):
    """Schema para crear un nuevo registro — sin foto_url (se sube aparte)"""
    pass


class PersonalUpdate(PersonalBase):
    """Schema para actualizar — todos los campos opcionales"""
    apellido_paterno:   Optional[str] = None
    apellido_materno:   Optional[str] = None
    nombres:            Optional[str] = None
    dni:                Optional[str] = None
    sexo:               Optional[SexoEnum] = None
    fecha_nacimiento:   Optional[date] = None
    estado_civil:       Optional[EstadoCivilEnum] = None
    nac_departamento:   Optional[str] = None
    nac_provincia:      Optional[str] = None
    nac_distrito:       Optional[str] = None
    celular:            Optional[str] = None
    email_personal_1:   Optional[EmailStr] = None
    dom_direccion:      Optional[str] = None


class PersonalResponse(PersonalBase):
    """Schema de respuesta — incluye campos generados por la BD"""
    id:            int
    foto_url:      Optional[str] = None
    creado_en:     datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


# ── Schema: DatosLaborales ─────────────────────────────────

class DatosLaboralesBase(BaseModel):
    dependencia:          str
    cargo:                str
    fecha_ingreso:        date
    email_institucional:  EmailStr
    condicion:            CondicionEnum
    tipo_personal:        TipoPersonalEnum

    # ── Régimen reestructurado ─────────────────────────────
    categoria_regimen:    Optional[CategoriaRegimenEnum]   = None
    regimen_dl276:        Optional[RegimenDL276Enum]       = None
    regimen_cas:          Optional[RegimenCASEnum]         = None
    regimen_ordinario:    Optional[RegimenOrdinarioEnum]   = None
    regimen_contratado:   Optional[RegimenContratadoEnum]  = None
    regimen_otros:        Optional[str]                    = None

    # ── Nivel y dedicación ─────────────────────────────────
    nivel_remunerativo:   Optional[NivelRemunerativoEnum]  = None
    dedicacion:           Optional[DedicacionEnum]         = None
    horas_semanales:      Optional[int]                    = None

    # ── RENACYT ────────────────────────────────────────────
    es_renacyt:           bool                             = False
    renacyt_codigo:       Optional[str]                    = None
    renacyt_nivel:        Optional[NivelRenacytEnum]       = None
    renacyt_activo:       bool                             = True

    @field_validator("email_institucional")
    @classmethod
    def validar_email_institucional(cls, v):
        if not str(v).endswith("@unamba.edu.pe"):
            raise ValueError(
                "El correo institucional debe terminar en @unamba.edu.pe"
            )
        return v

    @model_validator(mode="after")
    def validar_un_subregimen(self):
        activos = sum([
            self.regimen_dl276      is not None,
            self.regimen_cas        is not None,
            self.regimen_ordinario  is not None,
            self.regimen_contratado is not None,
        ])
        if activos > 1:
            raise ValueError(
                "Solo puede tener un sub-régimen activo a la vez"
            )
        return self

    @model_validator(mode="after")
    def validar_horas(self):
        if self.dedicacion == DedicacionEnum.horas and not self.horas_semanales:
            raise ValueError(
                "Debe especificar las horas semanales cuando la dedicación es por Horas"
            )
        return self

    @model_validator(mode="after")
    def validar_renacyt(self):
        if self.es_renacyt:
            if self.tipo_personal != TipoPersonalEnum.docente:
                raise ValueError("RENACYT solo aplica a personal docente")
            if not self.renacyt_codigo or not self.renacyt_nivel:
                raise ValueError(
                    "Debe ingresar código y nivel RENACYT si es investigador"
                )
        return self


class DatosLaboralesCreate(DatosLaboralesBase):
    pass

class DatosLaboralesUpdate(DatosLaboralesBase):
    dependencia:         Optional[str]            = None
    cargo:               Optional[str]            = None
    fecha_ingreso:       Optional[date]           = None
    email_institucional: Optional[EmailStr]       = None
    condicion:           Optional[CondicionEnum]  = None
    tipo_personal:       Optional[TipoPersonalEnum] = None

class DatosLaboralesResponse(DatosLaboralesBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


# ── Schema: Familiar ───────────────────────────────────────

class FamiliarBase(BaseModel):
    apellido_paterno:    str
    apellido_materno:    str
    nombres:             str
    parentesco:          ParentescoEnum
    dni:                 Optional[str] = None
    fecha_nacimiento:    Optional[date] = None
    sexo:                Optional[SexoEnum] = None
    nac_pais:            str = "Perú"
    nac_departamento:    Optional[str] = None
    nac_provincia:       Optional[str] = None
    nac_distrito:        Optional[str] = None
    nac_anexo:           Optional[str] = None
    vive_con_trabajador: bool = False

    @field_validator("dni")
    @classmethod
    def validar_dni_familiar(cls, v):
        if v is not None and not re.match(r"^\d{8}$", v):
            raise ValueError("El DNI del familiar debe tener 8 dígitos numéricos")
        return v


class FamiliarCreate(FamiliarBase):
    pass

class FamiliarUpdate(FamiliarBase):
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    nombres:          Optional[str] = None
    parentesco:       Optional[ParentescoEnum] = None

class FamiliarResponse(FamiliarBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}