from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notificacion(Base):
    __tablename__ = "notificacion"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    mensaje = Column(Text, nullable=False)
    leido = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, nullable=False)

    orden_servicio_id = Column(Integer, ForeignKey("orden_servicio.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=True)
    mecanico_id = Column(Integer, ForeignKey("mecanico.id"), nullable=True)

    orden_servicio = relationship("OrdenServicio", back_populates="notificaciones")
    admin = relationship("Admin", backref="notificaciones")
    cliente = relationship("Cliente", backref="notificaciones")
    mecanico = relationship("Mecanico", backref="notificaciones")
