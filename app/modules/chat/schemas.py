from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MensajeCreate(BaseModel):
    contenido: str
    orden_servicio_id: int


class MensajeEdit(BaseModel):
    contenido: str


class MensajeResponse(BaseModel):
    id: int
    contenido: str
    fecha_hora: datetime
    editado: bool = False
    fecha_edicion: Optional[datetime] = None
    orden_servicio_id: int
    remitente_id: int
    remitente_nombre: str
    remitente_rol: str

    model_config = {"from_attributes": True}


class EvidenciaResponse(BaseModel):
    id: int
    url: str
    fecha: datetime
    orden_servicio_id: int
    mensaje_id: Optional[int] = None

    model_config = {"from_attributes": True}
