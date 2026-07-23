from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class CatalogoMoto(Base):
    __tablename__ = "catalogo_moto"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    gama_color = Column(String(100), nullable=False)
    logo_url = Column(Text, nullable=True)

    motos_cliente = relationship("MotoCliente", back_populates="catalogo_moto")


class MotoCliente(Base):
    __tablename__ = "moto_cliente"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(20), unique=True, index=True, nullable=False)
    anio = Column(Integer, nullable=False)
    color = Column(String(50), nullable=True)
    codigo_qr = Column(Text, nullable=True)

    catalogo_moto_id = Column(Integer, ForeignKey("catalogo_moto.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)

    catalogo_moto = relationship("CatalogoMoto", back_populates="motos_cliente")
    cliente = relationship("Cliente", backref="motos_cliente")
    ordenes_servicio = relationship("OrdenServicio", back_populates="moto_cliente")
    historial_mantenimiento = relationship("HistorialMantenimiento", back_populates="moto_cliente")


class Marca(Base):
    __tablename__ = "marca"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    logo_url = Column(Text, nullable=True)


class HistorialMantenimiento(Base):
    __tablename__ = "historial_mantenimiento"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime, nullable=False)

    moto_cliente_id = Column(Integer, ForeignKey("moto_cliente.id"), nullable=False)
    orden_servicio_id = Column(Integer, ForeignKey("orden_servicio.id"), nullable=False)
    mecanico_id = Column(Integer, ForeignKey("mecanico.id"), nullable=False)

    moto_cliente = relationship("MotoCliente", back_populates="historial_mantenimiento")
    orden_servicio = relationship("OrdenServicio", backref="historial_mantenimiento")
    mecanico = relationship("Mecanico", backref="historial_mantenimiento")
