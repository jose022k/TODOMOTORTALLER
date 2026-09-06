from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FaqCreate(BaseModel):
    servicio: Optional[str] = ""
    pregunta: str
    respuesta: str
    monto_euro: float
    es_precio_minimo: Optional[bool] = False
    orden: Optional[int] = 0


class FaqUpdate(BaseModel):
    servicio: Optional[str] = None
    pregunta: Optional[str] = None
    respuesta: Optional[str] = None
    monto_euro: Optional[float] = None
    es_precio_minimo: Optional[bool] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None


class FaqResponse(BaseModel):
    id: int
    servicio: str
    pregunta: str
    respuesta: str
    monto_euro: float
    es_precio_minimo: bool
    orden: int
    activo: bool
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
