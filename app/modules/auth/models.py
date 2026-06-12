import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    contraseña = Column(String(255), nullable=False)


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    cedula = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=False)
    direccion = Column(Text, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)


class Mecanico(Base):
    __tablename__ = "mecanico"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
