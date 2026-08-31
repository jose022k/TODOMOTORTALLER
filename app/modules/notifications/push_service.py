import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException
from app.core.config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_CLAIMS
from app.modules.notifications.dao import PushSubscriptionDAO

sub_dao = PushSubscriptionDAO()


def subscribe(db: Session, subscription: dict, current_user):
    endpoint = subscription.get("endpoint")
    keys = subscription.get("keys", {})
    if not endpoint or not keys.get("p256dh") or not keys.get("auth"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suscripción inválida")

    existing = sub_dao.get_by_endpoint(db, endpoint)
    if existing:
        return existing

    field = {"admin": "admin_id", "cliente": "cliente_id", "mecanico": "mecanico_id"}.get(current_user.rol)
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


def send_push(subscription, title: str, body: str, icon: str = None, url: str = None):
    payload = json.dumps({
        "title": title,
        "body": body,
        "icon": icon or "/img/icons/logo-192.png",
        "badge": "/img/icons/logo-192.png",
        "data": {"url": url or "/"},
    })
    try:
        sub_info = {
            "endpoint": subscription.endpoint,
            "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
        }
        webpush(
            subscription_info=sub_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS,
        )
    except WebPushException as e:
        if e.response and e.response.status_code in (410, 404):
            return False
    return True


def notify_user(db: Session, user_id: int, role: str, title: str, body: str, url: str = None):
    subs = sub_dao.get_by_user(db, user_id, role)
    stale = []
    for sub in subs:
        ok = send_push(sub, title, body, url=url)
        if ok is False:
            stale.append(sub)
    for s in stale:
        sub_dao.delete(db, s)
