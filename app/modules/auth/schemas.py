import re
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator

# Solo números: cédula venezolana de 6 a 11 dígitos, teléfono con 11 dígitos (04121234567)
RE_CEDULA = re.compile(r"^\d{6,11}$")
RE_TELEFONO = re.compile(r"^\d{11}$")
RE_SOLO_NUMEROS = re.compile(r"^\d+$")


def _validar_nombre_completo(valor: str) -> str:
    """Exige nombre y apellido (dos palabras como mínimo)."""
    valor = (valor or "").strip()
    if not valor:
        raise ValueError("El nombre y apellido es obligatorio.")
    if len(valor.split()) < 2:
        raise ValueError("Debes agregar tu apellido (nombre y apellido).")
    return valor


def _validar_cedula(valor: str) -> str:
    valor = (valor or "").strip()
    if not valor:
        raise ValueError("La cédula es obligatoria.")
    if not RE_SOLO_NUMEROS.match(valor):
        raise ValueError("La cédula debe contener solo números.")
    if not RE_CEDULA.match(valor):
        raise ValueError("La cédula debe tener entre 6 y 11 dígitos.")
    return valor


def _validar_telefono(valor: str) -> str:
    valor = (valor or "").strip()
    if not valor:
        raise ValueError("El teléfono es obligatorio.")
    if not RE_SOLO_NUMEROS.match(valor):
        raise ValueError("El teléfono debe contener solo números.")
    if not RE_TELEFONO.match(valor):
        raise ValueError("El teléfono debe tener exactamente 11 dígitos.")
    return valor


def _validar_direccion(valor: str) -> str:
    valor = (valor or "").strip()
    if not valor:
        raise ValueError("La dirección es obligatoria.")
    return valor


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

    @field_validator("nombre")
    @classmethod
    def _nombre(cls, v: str) -> str:
        return _validar_nombre_completo(v)

    @field_validator("cedula")
    @classmethod
    def _cedula(cls, v: str) -> str:
        return _validar_cedula(v)

    @field_validator("telefono")
    @classmethod
    def _telefono(cls, v: str) -> str:
        return _validar_telefono(v)

    @field_validator("direccion")
    @classmethod
    def _direccion(cls, v: str) -> str:
        return _validar_direccion(v)

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


class GoogleAuthRequest(BaseModel):
    access_token: Optional[str] = None
    credential_token: Optional[str] = None  # retrocompatibilidad


class GoogleCompleteProfileRequest(BaseModel):
    access_token: Optional[str] = None
    credential_token: Optional[str] = None  # retrocompatibilidad
    cedula: str
    nombre: str
    telefono: str
    direccion: str

    @field_validator("nombre")
    @classmethod
    def _nombre(cls, v: str) -> str:
        return _validar_nombre_completo(v)

    @field_validator("cedula")
    @classmethod
    def _cedula(cls, v: str) -> str:
        return _validar_cedula(v)

    @field_validator("telefono")
    @classmethod
    def _telefono(cls, v: str) -> str:
        return _validar_telefono(v)

    @field_validator("direccion")
    @classmethod
    def _direccion(cls, v: str) -> str:
        return _validar_direccion(v)


class GoogleAuthResponse(BaseModel):
    needs_profile_completion: bool = False
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

