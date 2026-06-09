from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Mensaje(Base):
    __tablename__ = "mensaje"

    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    fecha_hora = Column(DateTime, nullable=False)

    orden_servicio_id = Column(Integer, ForeignKey("orden_servicio.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=True)
    mecanico_id = Column(Integer, ForeignKey("mecanico.id"), nullable=True)

    orden_servicio = relationship("OrdenServicio", back_populates="mensajes")
    admin = relationship("Admin", backref="mensajes")
    cliente = relationship("Cliente", backref="mensajes")
    mecanico = relationship("Mecanico", backref="mensajes")
