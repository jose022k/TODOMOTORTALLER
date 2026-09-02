from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_serializer


class OrdenServicioBase(BaseModel):
    descripcion: str
    cliente_id: int
    mecanico_id: int
    monto: float
    moneda: str


class OrdenServicioCreate(OrdenServicioBase):
    # Para usar una moto ya registrada del cliente
    moto_cliente_id: Optional[int] = None
    # Para registrar una nueva moto desde el catálogo al crear la orden
    catalogo_moto_id: Optional[int] = None
    placa: Optional[str] = None
    anio: Optional[int] = None
    color: Optional[str] = None


class OrdenServicioUpdate(BaseModel):
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    fecha_cierre: Optional[datetime] = None
    mecanico_id: Optional[int] = None


class OrdenServicioResponse(BaseModel):
    id: int
    descripcion: str
    estado: str
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    monto: Optional[float] = None
    moneda: Optional[str] = None
    tasa_bcv: Optional[float] = None
    monto_usd: Optional[float] = None
    cliente_id: int
    mecanico_id: int
    moto_cliente_id: int

    model_config = {"from_attributes": True}

    @field_serializer("fecha_creacion", "fecha_cierre", check_fields=False)
    def serialize_dt(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()


class OrdenServicioListResponse(BaseModel):
    """Respuesta para listado de órdenes con nombres de relaciones."""
    id: int
    descripcion: str
    estado: str
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    monto: Optional[float] = None
    moneda: Optional[str] = None
    tasa_bcv: Optional[float] = None
    monto_usd: Optional[float] = None
    cliente_id: int
    cliente_nombre: str
    mecanico_id: int
    mecanico_nombre: str
    moto_cliente_id: int
    moto_placa: str
    moto_anio: Optional[int] = None
    moto_color_especifico: Optional[str] = None
    moto_marca: str
    moto_modelo: str
    moto_color: str

    @field_serializer("fecha_creacion", "fecha_cierre", check_fields=False)
    def serialize_dt(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()


class OrdenServicioDetailResponse(BaseModel):
    """Respuesta detallada con toda la información de la orden y sus relaciones."""
    id: int
    descripcion: str
    estado: str
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    monto: Optional[float] = None
    moneda: Optional[str] = None
    tasa_bcv: Optional[float] = None
    monto_usd: Optional[float] = None
    cliente_id: int
    cliente_nombre: str
    cliente_cedula: str
    mecanico_id: int
    mecanico_nombre: str
    moto_cliente_id: int
    moto_placa: str
    moto_anio: int
    moto_color_especifico: Optional[str] = None
    moto_marca: str
    moto_modelo: str
    moto_color: str

    @field_serializer("fecha_creacion", "fecha_cierre", check_fields=False)
    def serialize_dt(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat() + "Z" if dt.tzinfo is None else dt.isoformat()


class MechanicAssign(BaseModel):
    mecanico_id: int


class StatusUpdate(BaseModel):
    estado: str


class EvidenciaBase(BaseModel):
    url: str
    fecha: datetime
    orden_servicio_id: int
    mensaje_id: Optional[int] = None


class EvidenciaCreate(EvidenciaBase):
    pass


class EvidenciaResponse(EvidenciaBase):
    id: int

    model_config = {"from_attributes": True}
