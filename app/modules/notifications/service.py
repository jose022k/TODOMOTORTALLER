from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.modules.notifications.dao import NotificacionDAO
from app.modules.notifications.schemas import NotificacionResponse
from app.modules.notifications.push_service import notify_user

notificacion_dao = NotificacionDAO()


def _build_response(n) -> NotificacionResponse:
    return NotificacionResponse(
        id=n.id,
        tipo=n.tipo,
        mensaje=n.mensaje,
        leido=n.leido,
        fecha_creacion=n.fecha_creacion,
        orden_servicio_id=n.orden_servicio_id,
        admin_id=n.admin_id,
        cliente_id=n.cliente_id,
        mecanico_id=n.mecanico_id,
    )


def get_notifications(db: Session, current_user, skip: int = 0, limit: int = 50):
    notifs = notificacion_dao.get_by_user(db, current_user.id, current_user.rol, skip=skip, limit=limit)
    unread = notificacion_dao.get_unread_count(db, current_user.id, current_user.rol)
    return [_build_response(n) for n in notifs], unread


def mark_read(db: Session, notif_id: int, current_user) -> Optional[NotificacionResponse]:
    notif = notificacion_dao.mark_as_read(db, notif_id, current_user.id, current_user.rol)
    if not notif:
        return None
    return _build_response(notif)


def mark_all_read(db: Session, current_user) -> int:
    return notificacion_dao.mark_all_as_read(db, current_user.id, current_user.rol)


def delete_all(db: Session, current_user) -> int:
    return notificacion_dao.delete_all(db, current_user.id, current_user.rol)


def create_notification(
    db: Session,
    tipo: str,
    mensaje: str,
    orden_servicio_id: Optional[int] = None,
    admin_id: Optional[int] = None,
    cliente_id: Optional[int] = None,
    mecanico_id: Optional[int] = None,
    open_chat: bool = False,
):
    data = {
        "tipo": tipo,
        "mensaje": mensaje,
        "leido": False,
        "fecha_creacion": datetime.utcnow(),
        "orden_servicio_id": orden_servicio_id,
        "admin_id": admin_id,
        "cliente_id": cliente_id,
        "mecanico_id": mecanico_id,
    }
    result = notificacion_dao.create(db, data)

    extra = "&open_chat=1" if open_chat else ""

    # También enviar Web Push si hay un destinatario
    try:
        if admin_id:
            url = f"/admin/service-orders?order_id={orden_servicio_id}{extra}" if orden_servicio_id else "/"
            notify_user(db, admin_id, "admin", "Todomotortaller", mensaje, url)
        if cliente_id:
            if orden_servicio_id and open_chat:
                url = f"/cliente/orders?order_id={orden_servicio_id}&open_chat=1"
            elif orden_servicio_id:
                url = f"/tracker/{orden_servicio_id}"
            else:
                url = "/cliente/orders"
            notify_user(db, cliente_id, "cliente", "Todomotortaller", mensaje, url)
        if mecanico_id:
            url = f"/mecanico/orders?order_id={orden_servicio_id}{extra}" if orden_servicio_id else "/"
            notify_user(db, mecanico_id, "mecanico", "Todomotortaller", mensaje, url)
    except Exception:
        pass

    return result
