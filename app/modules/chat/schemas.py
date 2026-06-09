from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MensajeBase(BaseModel):
    contenido: str
    fecha_hora: datetime
    orden_servicio_id: int
    admin_id: Optional[int] = None
    cliente_id: Optional[int] = None
    mecanico_id: Optional[int] = None


class MensajeCreate(MensajeBase):
    pass


class MensajeResponse(MensajeBase):
    id: int

    model_config = {"from_attributes": True}
