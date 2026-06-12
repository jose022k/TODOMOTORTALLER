from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    nombre: str
    password: str
    rol: str = "cliente"

class AdminCreate(UserCreate):
    pass

class ClienteCreate(UserCreate):
    cedula: str
    telefono: str
    direccion: str

class MecanicoCreate(UserCreate):
    pass


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    rol: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    nombre: str
    rol: str
    cedula: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = True

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    password: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
