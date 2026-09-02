from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.ws_manager import manager
from app.modules.auth.utils import decode_token
from app.modules.auth.models import Admin, Cliente, Mecanico
from app.modules.auth.service import get_user_by_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/socket/orders")
async def websocket_orders(
    websocket: WebSocket,
    token: str = Query(...),
):
    user = None
    try:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            await websocket.close(code=4001)
            return

        user_id = payload.get("sub")
        role = payload.get("role")
        jti = payload.get("jti")

        from app.core.database import SessionLocal
        from app.modules.auth.service import validate_active_session
        db = SessionLocal()
        try:
            user = get_user_by_id(db, user_id, role)
            if not user:
                await websocket.close(code=4001)
                return
            if jti and not validate_active_session(db, user.id, role, jti):
                await websocket.close(code=4001)
                return
        finally:
            db.close()

        await manager.connect(websocket, user.id, user.rol)

        # Keep connection alive and listen for client pings
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user:
            manager.disconnect(websocket, user.id, user.rol)
