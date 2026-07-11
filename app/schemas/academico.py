# Schemas Pydantic para formación, experiencia y reconocimientos
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, model_validator
from app.models.academico import (
    NivelEducativoEnum, EstadoEstudioEnum,
    TipoOtroEstudioEnum, TipoConstanciaEnum,
    TipoInstitucionEnum,
)


# ── Schema: FormacionAcademica ─────────────────────────────

class FormacionAcademicaBase(BaseModel):
    nivel:              NivelEducativoEnum
    estado:             EstadoEstudioEnum
    centro_estudios:    Optional[str] = None
    grado_obtenido:     Optional[str] = None
    mencion:            Optional[str] = None
    fecha_inicio:       Optional[date] = None
    fecha_conclusion:   Optional[date] = None
    documento_acredita: Optional[str] = None
    orden:              int = 1

    @model_validator(mode="after")
    def validar_centro_estudios(self):
        niveles_basicos = [
            NivelEducativoEnum.primaria,
            NivelEducativoEnum.secundaria,
        ]
        if self.nivel not in niveles_basicos and not self.centro_estudios:
            raise ValueError(
                "El centro de estudios es obligatorio para niveles superiores"
            )
        return self

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_inicio and self.fecha_conclusion:
            if self.fecha_conclusion < self.fecha_inicio:
                raise ValueError(
                    "La fecha de conclusión no puede ser anterior a la de inicio"
                )
        return self

    @model_validator(mode="after")
    def validar_orden(self):
        niveles_con_limite = [
            NivelEducativoEnum.bachiller,
            NivelEducativoEnum.titulo,
            NivelEducativoEnum.segunda_especialidad,
            NivelEducativoEnum.maestria,
            NivelEducativoEnum.doctorado,
        ]
        if self.nivel in niveles_con_limite and self.orden > 3:
            raise ValueError(
                f"El nivel {self.nivel} permite máximo 3 registros"
            )
        return self


class FormacionAcademicaCreate(FormacionAcademicaBase):
    pass

class FormacionAcademicaUpdate(FormacionAcademicaBase):
    nivel:  Optional[NivelEducativoEnum] = None
    estado: Optional[EstadoEstudioEnum] = None

class FormacionAcademicaResponse(FormacionAcademicaBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


# ── Schema: OtrosEstudios ──────────────────────────────────

class OtrosEstudiosBase(BaseModel):
    tipo:               TipoOtroEstudioEnum
    nombre_curso:       str
    centro_estudios:    str
    fecha_inicio:       Optional[date] = None
    fecha_fin:          Optional[date] = None
    fecha_emision:      Optional[date] = None
    duracion_horas:     Optional[int] = None
    tipo_constancia:    Optional[TipoConstanciaEnum] = None
    orden:              int = 1

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin < self.fecha_inicio:
                raise ValueError(
                    "La fecha de fin no puede ser anterior a la de inicio"
                )
        return self

    @model_validator(mode="after")
    def validar_orden(self):
        if self.orden < 1 or self.orden > 10:
            raise ValueError("El orden debe estar entre 1 y 10")
        return self


class OtrosEstudiosCreate(OtrosEstudiosBase):
    pass

class OtrosEstudiosUpdate(OtrosEstudiosBase):
    tipo:            Optional[TipoOtroEstudioEnum] = None
    nombre_curso:    Optional[str] = None
    centro_estudios: Optional[str] = None

class OtrosEstudiosResponse(OtrosEstudiosBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


# ── Schema: ExperienciaLaboral ─────────────────────────────

class ExperienciaLaboralBase(BaseModel):
    tipo_institucion:   TipoInstitucionEnum
    nombre_entidad:     str
    cargo:              str
    documento_acredita: Optional[str] = None
    fecha_inicio:       date
    fecha_culminacion:  Optional[date] = None
    tiempo_cargo:       Optional[str] = None
    orden:              int = 1

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_inicio and self.fecha_culminacion:
            if self.fecha_culminacion < self.fecha_inicio:
                raise ValueError(
                    "La fecha de culminación no puede ser anterior a la de inicio"
                )
        return self

    @model_validator(mode="after")
    def validar_orden(self):
        if self.orden < 1 or self.orden > 10:
            raise ValueError("El orden debe estar entre 1 y 10")
        return self


class ExperienciaLaboralCreate(ExperienciaLaboralBase):
    pass

class ExperienciaLaboralUpdate(ExperienciaLaboralBase):
    tipo_institucion: Optional[TipoInstitucionEnum] = None
    nombre_entidad:   Optional[str] = None
    cargo:            Optional[str] = None
    fecha_inicio:     Optional[date] = None

class ExperienciaLaboralResponse(ExperienciaLaboralBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


# ── Schema: ExperienciaDocente ─────────────────────────────

class ExperienciaDocenteBase(BaseModel):
    nombre_entidad:     str
    categoria:          Optional[str] = None
    documento_acredita: Optional[str] = None
    fecha_inicio:       date
    fecha_culminacion:  Optional[date] = None
    tiempo_cargo:       Optional[str] = None
    orden:              int = 1

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_inicio and self.fecha_culminacion:
            if self.fecha_culminacion < self.fecha_inicio:
                raise ValueError(
                    "La fecha de culminación no puede ser anterior a la de inicio"
                )
        return self

    @model_validator(mode="after")
    def validar_orden(self):
        if self.orden < 1 or self.orden > 15:
            raise ValueError("El orden debe estar entre 1 y 15")
        return self


class ExperienciaDocenteCreate(ExperienciaDocenteBase):
    pass

class ExperienciaDocenteUpdate(ExperienciaDocenteBase):
    nombre_entidad: Optional[str] = None
    fecha_inicio:   Optional[date] = None

class ExperienciaDocenteResponse(ExperienciaDocenteBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


# ── Schema: OtrasInstituciones ─────────────────────────────

class OtrasInstitucionesBase(BaseModel):
    labora_otra_inst: bool = False
    tipo_personal:    Optional[str] = None
    nombre_entidad:   Optional[str] = None
    dia_lunes:        bool = False
    dia_martes:       bool = False
    dia_miercoles:    bool = False
    dia_jueves:       bool = False
    dia_viernes:      bool = False
    horas_diarias:    Optional[int] = None

    @model_validator(mode="after")
    def validar_datos_si_labora(self):
        if self.labora_otra_inst:
            if not self.nombre_entidad:
                raise ValueError(
                    "Debe especificar el nombre de la entidad "
                    "si labora en otra institución"
                )
            if not self.tipo_personal:
                raise ValueError(
                    "Debe especificar el tipo de personal "
                    "si labora en otra institución"
                )
        return self


class OtrasInstitucionesCreate(OtrasInstitucionesBase):
    pass

class OtrasInstitucionesUpdate(OtrasInstitucionesBase):
    labora_otra_inst: Optional[bool] = None

class OtrasInstitucionesResponse(OtrasInstitucionesBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


# ── Schema: Reconocimiento ─────────────────────────────────

class ReconocimientoBase(BaseModel):
    nombre_entidad:      str
    tipo_reconocimiento: str
    documento_acredita:  Optional[str] = None
    fecha_documento:     Optional[date] = None
    orden:               int = 1

    @model_validator(mode="after")
    def validar_orden(self):
        if self.orden < 1 or self.orden > 6:
            raise ValueError("El orden debe estar entre 1 y 6")
        return self


class ReconocimientoCreate(ReconocimientoBase):
    pass

class ReconocimientoUpdate(ReconocimientoBase):
    nombre_entidad:      Optional[str] = None
    tipo_reconocimiento: Optional[str] = None

class ReconocimientoResponse(ReconocimientoBase):
    id:             int
    personal_id:    int
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}