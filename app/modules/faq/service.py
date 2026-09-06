from typing import List
from sqlalchemy.orm import Session
from app.modules.faq.models import Faq
from app.modules.faq.schemas import FaqCreate, FaqUpdate


def get_all_faqs(db: Session, include_inactive: bool = False) -> List[Faq]:
    query = db.query(Faq)
    if not include_inactive:
        query = query.filter(Faq.activo == True)
    return query.order_by(Faq.orden.asc(), Faq.id.asc()).all()


def create_faq(db: Session, data: FaqCreate) -> Faq:
    faq = Faq(
        servicio=data.servicio,
        pregunta=data.pregunta,
        respuesta=data.respuesta,
        monto_euro=data.monto_euro,
        es_precio_minimo=data.es_precio_minimo if data.es_precio_minimo is not None else False,
        orden=data.orden if data.orden is not None else 0,
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


def update_faq(db: Session, faq_id: int, data: FaqUpdate) -> Faq:
    faq = db.query(Faq).filter(Faq.id == faq_id).first()
    if not faq:
        return None
    update_data = data.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(faq, field, val)
    db.commit()
    db.refresh(faq)
    return faq


def delete_faq(db: Session, faq_id: int) -> bool:
    faq = db.query(Faq).filter(Faq.id == faq_id).first()
    if not faq:
        return False
    db.delete(faq)
    db.commit()
    return True
