import json
import threading
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException
from app.core.config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_CLAIMS
from app.modules.notifications.dao import PushSubscriptionDAO

sub_dao = PushSubscriptionDAO()

# Tiempo máximo de espera por cada envío de push (evita colgar la petición)
PUSH_TIMEOUT_SEG = 8


def subscribe(db: Session, subscription: dict, current_user):
    endpoint = subscription.get("endpoint")
    keys = subscription.get("keys", {})
    if not endpoint or not keys.get("p256dh") or not keys.get("auth"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suscripción inválida")

    field = {"admin": "admin_id", "cliente": "cliente_id", "mecanico": "mecanico_id"}.get(current_user.rol)

    existing = sub_dao.get_by_endpoint(db, endpoint)
    if existing:
        setattr(existing, "admin_id", None)
        setattr(existing, "cliente_id", None)
        setattr(existing, "mecanico_id", None)
        setattr(existing, field, current_user.id)
        existing.p256dh = keys["p256dh"]
        existing.auth = keys["auth"]
        db.commit()
        db.refresh(existing)
        return existing

    data = {
        "endpoint": endpoint,
        "p256dh": keys["p256dh"],
        "auth": keys["auth"],
        field: current_user.id,
    }
    return sub_dao.create(db, data)


def unsubscribe(db: Session, endpoint: str, current_user):
    sub = sub_dao.get_by_endpoint(db, endpoint)
    if not sub:
        return
    field = {"admin": "admin_id", "cliente": "cliente_id", "mecanico": "mecanico_id"}.get(current_user.rol)
    if getattr(sub, field) == current_user.id:
        sub_dao.delete(db, sub)


def _build_payload(title: str, body: str, icon: str = None, url: str = None, unread_count: int = 0) -> str:
    return json.dumps({
        "title": title,
        "body": body,
        "icon": icon or "/img/app-icon-192.png",
        "badge": "/img/app-icon-192.png",
        "sound": "/sounds/notification.wav",
        "data": {
            "url": url or "/",
            "unread_count": unread_count,
            "id": str(int(datetime.utcnow().timestamp() * 1000))
        },
    })


def _send_push_info(sub_info: dict, title: str, body: str, icon: str = None, url: str = None, unread_count: int = 0) -> str:
    """Envía un push a una suscripción ya serializada. Nunca lanza excepciones."""
    payload = _build_payload(title, body, icon, url, unread_count)
    try:
        webpush(
            subscription_info=sub_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
            ttl=86400,
            headers={"Urgency": "high", "TTL": "86400"},
            timeout=PUSH_TIMEOUT_SEG,
        )
        return "ok"
    except WebPushException as e:
        if e.response is not None and e.response.status_code in (404, 410):
            return "stale"
        return "error"
    except Exception:
        return "error"


def send_push(subscription, title: str, body: str, icon: str = None, url: str = None, unread_count: int = 0) -> str:
    """Envía un push de forma síncrona (bloquea hasta PUSH_TIMEOUT_SEG)."""
    sub_info = {
        "endpoint": subscription.endpoint,
        "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
    }
    return _send_push_info(sub_info, title, body, icon=icon, url=url, unread_count=unread_count)


def _deliver_in_background(subs_info: list, title: str, body: str, url: str, unread_count: int):
    """Hilo independiente: envía los pushes SIN bloquear la respuesta HTTP."""
    stale = []
    for info in subs_info:
        if _send_push_info(info, title, body, url=url, unread_count=unread_count) == "stale":
            stale.append(info)

    if not stale:
        return
    # Limpia las suscripciones muertas usando una sesión propia de BD
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            dao = PushSubscriptionDAO()
            for info in stale:
                sub = dao.get_by_endpoint(db, info["endpoint"])
                if sub:
                    dao.delete(db, sub)
        finally:
            db.close()
    except Exception:
        pass


def notify_user(db: Session, user_id: int, role: str, title: str, body: str, url: str = None, unread_count: int = 0):
    """Recoge las suscripciones del usuario y lanza el envío en segundo plano.

    El push se entrega en un hilo aparte para que crear/cancelar/iniciar una
    orden responda de inmediato al usuario.
    """
    subs = sub_dao.get_by_user(db, user_id, role)
    if not subs:
        return

    subs_info = [
        {"endpoint": s.endpoint, "keys": {"p256dh": s.p256dh, "auth": s.auth}}
        for s in subs
    ]
    threading.Thread(
        target=_deliver_in_background,
        args=(subs_info, title, body, url, unread_count),
        daemon=True,
    ).start()
