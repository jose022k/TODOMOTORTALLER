from datetime import datetime
from typing import List, Optional
import threading
from sqlalchemy.orm import Session
from app.modules.notifications.dao import NotificacionDAO
from app.modules.notifications.models import Notificacion
from app.modules.notifications.schemas import NotificacionResponse
from app.modules.notifications.push_service import notify_user
from app.modules.preferences.service import should_notify, allowed_tipos

notificacion_dao = NotificacionDAO()


def create_notifications_in_background(specs: List[dict]):
    """Crea varias notificaciones en un hilo con su propia sesión de BD.

    Permite que la petición HTTP responda de inmediato, sin esperar a escribir
    cada notificación (varias idas y vueltas a la base de datos) ni a enviar
    los pushes. Si algo falla, las notificaciones se descartan en silencio.
    """
    if not specs:
        return

    def _run():
        try:
            from app.core.database import SessionLocal
            db = SessionLocal()
            try:
                for spec in specs:
                    create_notification(db, commit=True, **spec)
            finally:
                db.close()
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


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
    commit: bool = True,
):
    """Crea una notificación.

    commit=False deja el registro en la transacción actual (flush sin commit)
    para que el llamador pueda agrupar varias notificaciones en un solo commit.
    """
    # Preferencias de CADA destinatario por separado.
    # Antes, si el cliente tenía apagado un tipo de aviso, se descartaba la
    # notificación entera y el admin y el mecánico tampoco se enteraban.
    if admin_id and not should_notify(db, "admin", admin_id, tipo):
        admin_id = None
    if cliente_id and not should_notify(db, "cliente", cliente_id, tipo):
        cliente_id = None
    if mecanico_id and not should_notify(db, "mecanico", mecanico_id, tipo):
        mecanico_id = None

    if not (admin_id or cliente_id or mecanico_id):
        return None

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

    if commit:
        result = notificacion_dao.create(db, data)
    else:
        # Deja el registro en la transacción abierta sin confirmar.
        result = Notificacion(**data)
        db.add(result)
        db.flush()

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
