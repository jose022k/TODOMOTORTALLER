from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.core.base_dao import BaseDAO
from app.modules.service_orders.models import OrdenServicio, Evidencia
from app.modules.service_orders.schemas import OrdenServicioCreate, OrdenServicioUpdate
from app.modules.motorcycles.models import MotoCliente


class OrdenServicioDAO(BaseDAO[OrdenServicio, OrdenServicioCreate, OrdenServicioUpdate]):
    def __init__(self):
        super().__init__(OrdenServicio)

    def get_by_cliente(self, db: Session, cliente_id: int) -> List[OrdenServicio]:
        return (
            db.query(self.model)
            .filter(self.model.cliente_id == cliente_id)
            .order_by(self.model.fecha_creacion.desc())
            .all()
        )

    def get_by_mecanico(self, db: Session, mecanico_id: int) -> List[OrdenServicio]:
        return (
            db.query(self.model)
            .filter(self.model.mecanico_id == mecanico_id)
            .order_by(self.model.fecha_creacion.desc())
            .all()
        )

    def get_all_with_relations(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        estado: Optional[str] = None,
        cliente_id: Optional[int] = None,
        mecanico_id: Optional[int] = None,
        moto_cliente_id: Optional[int] = None,
    ) -> List[OrdenServicio]:
        query = (
            db.query(self.model)
            .options(
                joinedload(self.model.cliente),
                joinedload(self.model.mecanico),
                joinedload(self.model.moto_cliente).joinedload(MotoCliente.catalogo_moto),
            )
            .order_by(self.model.fecha_creacion.desc())
        )
        if estado:
            query = query.filter(self.model.estado == estado)
        if cliente_id is not None:
            query = query.filter(self.model.cliente_id == cliente_id)
        if mecanico_id is not None:
            query = query.filter(self.model.mecanico_id == mecanico_id)
        if moto_cliente_id is not None:
            query = query.filter(self.model.moto_cliente_id == moto_cliente_id)

        return query.offset(skip).limit(limit).all()


class EvidenciaDAO(BaseDAO[Evidencia, OrdenServicioCreate, OrdenServicioUpdate]):
    def __init__(self):
        super().__init__(Evidencia)

    def get_by_orden(self, db: Session, orden_id: int) -> List[Evidencia]:
        return (
            db.query(self.model)
            .filter(self.model.orden_servicio_id == orden_id)
            .order_by(self.model.fecha.desc())
            .all()
        )
