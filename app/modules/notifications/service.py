from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.modules.notifications.dao import NotificacionDAO
from app.modules.notifications.schemas import NotificacionResponse
from app.modules.notifications.push_service import notify_user
from app.modules.preferences.service import should_notify, allowed_tipos

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
    allowed = allowed_tipos(db, current_user.rol, current_user.id)
    notifs = notificacion_dao.get_by_user(db, current_user.id, current_user.rol, skip=skip, limit=limit, allowed_tipos=allowed)
    unread = notificacion_dao.get_unread_count(db, current_user.id, current_user.rol, allowed_tipos=allowed)
    return [_build_response(n) for n in notifs], unread


def get_unread_count(db: Session, current_user) -> int:
    allowed = allowed_tipos(db, current_user.rol, current_user.id)
    return notificacion_dao.get_unread_count(db, current_user.id, current_user.rol, allowed_tipos=allowed)


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
    extra = "&open_chat=1" if open_chat else ""

    # Verificar preferencias antes de notificar
    if admin_id and not should_notify(db, "admin", admin_id, tipo):
        return None
    if cliente_id and not should_notify(db, "cliente", cliente_id, tipo):
        return None
    if mecanico_id and not should_notify(db, "mecanico", mecanico_id, tipo):
        return None

    result = notificacion_dao.create(db, data)

    # WebSocket: notificación instantánea
    try:
        targets = []
        if admin_id:
            targets.append((admin_id, "admin"))
        if cliente_id:
            targets.append((cliente_id, "cliente"))
        if mecanico_id:
            targets.append((mecanico_id, "mecanico"))
        if targets:
            from app.core.ws_manager import manager
            manager.schedule_broadcast_notification(_build_response(result).model_dump(mode="json"), targets)
    except Exception:
        pass

    # También enviar Web Push si hay un destinatario
    try:
        from app.modules.notifications.dao import NotificacionDAO
        from app.modules.preferences.service import allowed_tipos
        dao = NotificacionDAO()

        if admin_id:
            url = f"/admin/service-orders?order_id={orden_servicio_id}{extra}" if orden_servicio_id else "/"
            allowed = allowed_tipos(db, "admin", admin_id)
            unread_count = dao.get_unread_count(db, admin_id, "admin", allowed)
            notify_user(db, admin_id, "admin", "Todomotortaller", mensaje, url, unread_count=unread_count)
        if cliente_id:
            if orden_servicio_id and open_chat:
                url = f"/cliente/orders?order_id={orden_servicio_id}&open_chat=1"
            elif orden_servicio_id:
                url = f"/tracker/{orden_servicio_id}"
            else:
                url = "/cliente/orders"
            allowed = allowed_tipos(db, "cliente", cliente_id)
            unread_count = dao.get_unread_count(db, cliente_id, "cliente", allowed)
            notify_user(db, cliente_id, "cliente", "Todomotortaller", mensaje, url, unread_count=unread_count)
        if mecanico_id:
            url = f"/mecanico/orders?order_id={orden_servicio_id}{extra}" if orden_servicio_id else "/"
            allowed = allowed_tipos(db, "mecanico", mecanico_id)
            unread_count = dao.get_unread_count(db, mecanico_id, "mecanico", allowed)
            notify_user(db, mecanico_id, "mecanico", "Todomotortaller", mensaje, url, unread_count=unread_count)
    except Exception:
        pass

    return result
