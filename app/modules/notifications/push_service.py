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


def send_push(subscription, title: str, body: str, icon: str = None, url: str = None, unread_count: int = 0):
    payload = json.dumps({
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
            ttl=86400,
            headers={"Urgency": "high", "TTL": "86400"},
        )
        return "ok"
    except WebPushException as e:
        if e.response is not None and e.response.status_code in (404, 410):
            return "stale"
        return "error"
    except Exception:
        return "error"


def notify_user(db: Session, user_id: int, role: str, title: str, body: str, url: str = None, unread_count: int = 0):
    subs = sub_dao.get_by_user(db, user_id, role)
    stale = []
    for sub in subs:
        res = send_push(sub, title, body, url=url, unread_count=unread_count)
        if res == "stale":
            stale.append(sub)
    for s in stale:
        try:
            sub_dao.delete(db, s)
        except Exception:
            pass
