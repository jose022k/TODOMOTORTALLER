from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificacionBase(BaseModel):
    tipo: str
    mensaje: str
    orden_servicio_id: Optional[int] = None
    admin_id: Optional[int] = None
    cliente_id: Optional[int] = None
    mecanico_id: Optional[int] = None


class NotificacionCreate(NotificacionBase):
    pass


class NotificacionResponse(NotificacionBase):
    id: int
    leido: bool
    fecha_creacion: datetime

    model_config = {"from_attributes": True}
