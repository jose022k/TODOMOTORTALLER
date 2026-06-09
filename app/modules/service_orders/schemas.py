from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OrdenServicioBase(BaseModel):
    descripcion: str
    estado: str = "pendiente"
    cliente_id: int
    mecanico_id: int
    moto_cliente_id: int


class OrdenServicioCreate(OrdenServicioBase):
    pass


class OrdenServicioUpdate(BaseModel):
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    fecha_cierre: Optional[datetime] = None
    mecanico_id: Optional[int] = None


class OrdenServicioResponse(OrdenServicioBase):
    id: int
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None

    model_config = {"from_attributes": True}


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
