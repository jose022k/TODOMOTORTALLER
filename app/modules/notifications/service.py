import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.modules.notifications.dao import NotificacionDAO
from app.modules.notifications.schemas import NotificacionResponse
from app.modules.notifications.push_service import notify_user
from app.modules.preferences.service import should_notify, allowed_tipos

logger = logging.getLogger(__name__)
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

    logger.info(f"[NOTIF] create tipo={tipo} admin={admin_id} cliente={cliente_id} mecanico={mecanico_id}")

    # Verificar preferencias antes de notificar
    if admin_id and not should_notify(db, "admin", admin_id, tipo):
        logger.info(f"[NOTIF] Skipped admin {admin_id} - preferences disabled for {tipo}")
        return None
    if cliente_id and not should_notify(db, "cliente", cliente_id, tipo):
        logger.info(f"[NOTIF] Skipped cliente {cliente_id} - preferences disabled for {tipo}")
        return None
    if mecanico_id and not should_notify(db, "mecanico", mecanico_id, tipo):
        logger.info(f"[NOTIF] Skipped mecanico {mecanico_id} - preferences disabled for {tipo}")
        return None

    result = notificacion_dao.create(db, data)
    logger.info(f"[NOTIF] Created DB record id={result.id} tipo={tipo} admin={admin_id} cliente={cliente_id} mecanico={mecanico_id}")

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
            notif_dict = _build_response(result).model_dump(mode="json")
            manager.schedule_broadcast_notification(notif_dict, targets)
    except Exception as e:
        logger.error(f"[NOTIF] WS broadcast failed: {e}")

    # Enviar Web Push — cada destinatario aislado para no contaminar la sesión
    if admin_id:
        try:
            url = f"/admin/service-orders?order_id={orden_servicio_id}{extra}" if orden_servicio_id else "/"
            notify_user(db, admin_id, "admin", "Todomotortaller", mensaje, url)
        except Exception as e:
            print(f"[NOTIF] PUSH FAILED for admin {admin_id}: {e}")
            try:
                db.rollback()
            except Exception:
                pass
    if cliente_id:
        try:
            if orden_servicio_id and open_chat:
                url = f"/cliente/orders?order_id={orden_servicio_id}&open_chat=1"
            elif orden_servicio_id:
                url = f"/tracker/{orden_servicio_id}"
            else:
                url = "/cliente/orders"
            notify_user(db, cliente_id, "cliente", "Todomotortaller", mensaje, url)
        except Exception as e:
            print(f"[NOTIF] PUSH FAILED for cliente {cliente_id}: {e}")
            try:
                db.rollback()
            except Exception:
                pass
    if mecanico_id:
        try:
            url = f"/mecanico/orders?order_id={orden_servicio_id}{extra}" if orden_servicio_id else "/"
            notify_user(db, mecanico_id, "mecanico", "Todomotortaller", mensaje, url)
        except Exception as e:
            print(f"[NOTIF] PUSH FAILED for mecanico {mecanico_id}: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    return result
