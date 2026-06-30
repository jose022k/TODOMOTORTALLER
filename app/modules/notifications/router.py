from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, AnyUser
from app.modules.notifications.schemas import NotificacionResponse
from app.modules.notifications import service
from app.modules.notifications.push_service import subscribe, unsubscribe
from app.core.config import VAPID_PUBLIC_KEY

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificacionResponse])
def list_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    notifs, unread = service.get_notifications(db, current_user, skip=skip, limit=limit)
    response = Response()
    response.headers["X-Unread-Count"] = str(unread)
    return notifs


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    from app.modules.notifications.dao import NotificacionDAO
    count = NotificacionDAO().get_unread_count(db, current_user.id, current_user.rol)
    return {"count": count}


@router.put("/{notif_id}/read", response_model=NotificacionResponse)
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    result = service.mark_read(db, notif_id, current_user)
    if not result:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    return result


@router.put("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    count = service.mark_all_read(db, current_user)
    return {"marked": count}


@router.get("/push/vapid-public-key")
def get_vapid_public_key():
    return {"publicKey": VAPID_PUBLIC_KEY}


@router.post("/push/subscribe")
async def push_subscribe(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    import json
    body = json.loads(await request.body())
    sub = subscribe(db, body, current_user)
    return {"status": "subscribed", "id": sub.id}


@router.post("/push/unsubscribe")
async def push_unsubscribe(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    import json
    body = json.loads(await request.body())
    endpoint = body.get("endpoint")
    unsubscribe(db, endpoint, current_user)
    return {"status": "unsubscribed"}


@router.post("/push/close")
async def push_close(request: Request):
    import json
    try:
        body = json.loads(await request.body())
    except Exception:
        pass
    return {"status": "ok"}
