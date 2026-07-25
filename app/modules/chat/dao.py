from typing import List
from sqlalchemy.orm import Session, joinedload
from app.core.base_dao import BaseDAO
from app.modules.chat.models import Mensaje
from app.modules.chat.schemas import MensajeCreate


class MensajeDAO(BaseDAO[Mensaje, MensajeCreate, MensajeCreate]):
    def __init__(self):
        super().__init__(Mensaje)

    def get_by_orden(self, db: Session, orden_id: int) -> List[Mensaje]:
        return (
            db.query(self.model)
            .options(
                joinedload(self.model.admin),
                joinedload(self.model.cliente),
                joinedload(self.model.mecanico),
            )
            .filter(self.model.orden_servicio_id == orden_id)
            .order_by(self.model.fecha_hora.asc())
            .all()
        )
