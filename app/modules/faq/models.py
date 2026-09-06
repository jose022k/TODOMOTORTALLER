from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, func
from app.core.database import Base


class Faq(Base):
    __tablename__ = "faq"

    id = Column(Integer, primary_key=True, index=True)
    servicio = Column(String(255), nullable=False)
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    monto_euro = Column(Float, nullable=False, default=0.0)
    es_precio_minimo = Column(Boolean, nullable=False, default=False)
    orden = Column(Integer, nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
