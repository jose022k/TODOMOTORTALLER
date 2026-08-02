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
    color: Optional[str] = None
    marca: str
    modelo: str
    gama_color: str
    codigo_qr: Optional[str] = None


class ClienteSummary(BaseModel):
    """Versión ligera de ClienteResponse sin motos, para dropdowns."""
    id: int
    nombre: str
    cedula: str

    model_config = {"from_attributes": True}


class MecanicoResponse(BaseModel):
    id: int
    nombre: str
    email: str
    activo: bool = True

    model_config = {"from_attributes": True}


class ClienteResponse(BaseModel):
    id: int
    nombre: str
    cedula: str
    email: str
    telefono: str
    direccion: str
    activo: bool = True
    motos: list[MotoAsociada] = []

    model_config = {"from_attributes": True}


class CountResponse(BaseModel):
    total: int


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
