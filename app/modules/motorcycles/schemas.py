from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CatalogoMotoBase(BaseModel):
    marca: str
    modelo: str
    gama_color: str


class CatalogoMotoCreate(CatalogoMotoBase):
    pass


class CatalogoMotoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    gama_color: Optional[str] = None


class CatalogoMotoResponse(CatalogoMotoBase):
    id: int

    model_config = {"from_attributes": True}


class MotoClienteBase(BaseModel):
    placa: str
    anio: int
    catalogo_moto_id: int
    cliente_id: int


class MotoClienteCreate(MotoClienteBase):
    pass


class MotoClienteUpdate(BaseModel):
    placa: Optional[str] = None
    anio: Optional[int] = None
    catalogo_moto_id: Optional[int] = None


class MotoClienteResponse(MotoClienteBase):
    id: int
    codigo_qr: Optional[str] = None

    model_config = {"from_attributes": True}


class HistorialMantenimientoBase(BaseModel):
    descripcion: str
    fecha: datetime
    moto_cliente_id: int
    orden_servicio_id: int
    mecanico_id: int


class HistorialMantenimientoCreate(HistorialMantenimientoBase):
    pass


class HistorialMantenimientoResponse(HistorialMantenimientoBase):
    id: int

    model_config = {"from_attributes": True}
