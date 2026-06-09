from typing import Optional
from pydantic import BaseModel, EmailStr


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class MecanicoUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None


class MecanicoCreate(BaseModel):
    email: EmailStr
    nombre: str
    password: str


class MotoAsociada(BaseModel):
    id: int
    placa: str
    anio: int
    marca: str
    modelo: str
    gama_color: str
    codigo_qr: Optional[str] = None

    model_config = {"from_attributes": True}


class ClienteDetailResponse(BaseModel):
    id: int
    nombre: str
    cedula: str
    email: str
    telefono: str
    direccion: str
    activo: bool
    motos: list[MotoAsociada] = []

    model_config = {"from_attributes": True}
