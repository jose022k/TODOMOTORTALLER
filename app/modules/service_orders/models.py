from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrdenServicio(Base):
    __tablename__ = "orden_servicio"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)

    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    mecanico_id = Column(Integer, ForeignKey("mecanico.id"), nullable=False)
    moto_cliente_id = Column(Integer, ForeignKey("moto_cliente.id"), nullable=False)

    cliente = relationship("Cliente", backref="ordenes_servicio")
    mecanico = relationship("Mecanico", backref="ordenes_servicio")
    moto_cliente = relationship("MotoCliente", back_populates="ordenes_servicio")

    evidencias = relationship("Evidencia", back_populates="orden_servicio")
    mensajes = relationship("Mensaje", back_populates="orden_servicio")
    notificaciones = relationship("Notificacion", back_populates="orden_servicio")


class Evidencia(Base):
    __tablename__ = "evidencia"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False)
    fecha = Column(DateTime, nullable=False)

    orden_servicio_id = Column(Integer, ForeignKey("orden_servicio.id"), nullable=False)
    mensaje_id = Column(Integer, ForeignKey("mensaje.id"), nullable=True)

    orden_servicio = relationship("OrdenServicio", back_populates="evidencias")
    mensaje = relationship("Mensaje", backref="evidencias")
