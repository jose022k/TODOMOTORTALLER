from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.base_dao import BaseDAO
from app.modules.notifications.models import Notificacion, PushSubscription
from app.modules.notifications.schemas import NotificacionCreate


class NotificacionDAO(BaseDAO[Notificacion, NotificacionCreate, NotificacionCreate]):
    def __init__(self):
        super().__init__(Notificacion)

    def get_by_user(self, db: Session, user_id: int, role: str, skip: int = 0, limit: int = 50) -> List[Notificacion]:
        query = db.query(self.model)
        if role == "admin":
            query = query.filter(self.model.admin_id == user_id)
        elif role == "cliente":
            query = query.filter(self.model.cliente_id == user_id)
        elif role == "mecanico":
            query = query.filter(self.model.mecanico_id == user_id)
        return (
            query
            .order_by(self.model.fecha_creacion.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_unread_count(self, db: Session, user_id: int, role: str) -> int:
        query = db.query(self.model).filter(self.model.leido == False)
        if role == "admin":
            query = query.filter(self.model.admin_id == user_id)
        elif role == "cliente":
            query = query.filter(self.model.cliente_id == user_id)
        elif role == "mecanico":
            query = query.filter(self.model.mecanico_id == user_id)
        return query.count()

    def mark_as_read(self, db: Session, notif_id: int, user_id: int, role: str) -> Optional[Notificacion]:
        notif = self.get_by_id(db, notif_id)
        if not notif:
            return None
        field = {"admin": "admin_id", "cliente": "cliente_id", "mecanico": "mecanico_id"}.get(role)
        if not field or getattr(notif, field) != user_id:
            return None
        return self.update(db, notif, {"leido": True})

    def delete_all(self, db: Session, user_id: int, role: str) -> int:
        field = {"admin": "admin_id", "cliente": "cliente_id", "mecanico": "mecanico_id"}.get(role)
        if not field:
            return 0
        count = (
            db.query(self.model)
            .filter(getattr(self.model, field) == user_id)
            .delete(synchronize_session="fetch")
        )
        db.commit()
        return count

    def mark_all_as_read(self, db: Session, user_id: int, role: str) -> int:
        field = {"admin": "admin_id", "cliente": "cliente_id", "mecanico": "mecanico_id"}.get(role)
        if not field:
            return 0
        count = (
            db.query(self.model)
            .filter(getattr(self.model, field) == user_id, self.model.leido == False)
            .update({"leido": True}, synchronize_session="fetch")
        )
        db.commit()
        return count


class PushSubscriptionDAO:
    def get_by_user(self, db: Session, user_id: int, role: str) -> List[PushSubscription]:
        query = db.query(PushSubscription)
        if role == "admin":
            query = query.filter(PushSubscription.admin_id == user_id)
        elif role == "cliente":
            query = query.filter(PushSubscription.cliente_id == user_id)
        elif role == "mecanico":
            query = query.filter(PushSubscription.mecanico_id == user_id)
        return query.all()

    def get_by_endpoint(self, db: Session, endpoint: str) -> Optional[PushSubscription]:
        return db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).first()

    def create(self, db: Session, data: dict) -> PushSubscription:
        obj = PushSubscription(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, sub: PushSubscription):
        db.delete(sub)
        db.commit()
