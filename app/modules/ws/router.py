import asyncio
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.ws_manager import manager
from app.modules.auth.utils import decode_token
from app.modules.auth.models import Admin
from app.modules.auth.service import get_user_by_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# El cliente manda un "ping" cada 15 s. Si en este tiempo no llega nada,
# se da por muerta la conexión y se marca al usuario como "desconectado"
# al instante (no hace falta esperar a que la red avise).
CLIENTE_TIMEOUT_SEG = 60


def _avisar_escribiendo(user_id: int, rol: str, orden_id: int, escribiendo: bool):
    """Busca a los participantes de la orden y les avisa quién está escribiendo."""
    from app.core.database import SessionLocal
    from app.modules.service_orders.dao import OrdenServicioDAO

    db = SessionLocal()
    try:
        order = OrdenServicioDAO().get_by_id(db, orden_id)
        if not order:
            return

        targets = []
        if order.cliente_id and not (rol == "cliente" and order.cliente_id == user_id):
            targets.append((order.cliente_id, "cliente"))
        if order.mecanico_id and not (rol == "mecanico" and order.mecanico_id == user_id):
            targets.append((order.mecanico_id, "mecanico"))
        for aid in [a.id for a in db.query(Admin.id).all()]:
            if not (rol == "admin" and aid == user_id):
                targets.append((aid, "admin"))

        manager.schedule_broadcast_typing(orden_id, targets, user_id, rol, escribiendo)
    except Exception as e:
        logger.error(f"WS escribiendo: {e}")
    finally:
        db.close()


async def _procesar_mensaje_cliente(data: str, user_id: int, rol: str):
    """El navegador manda "ping" o eventos JSON (por ejemplo 'escribiendo')."""
    if not data or data == "ping" or not data.startswith("{"):
        return

    try:
        payload = json.loads(data)
    except ValueError:
        return

    if payload.get("tipo") not in ("escribiendo", "dejando_de_escribir"):
        return

    try:
        orden_id = int(payload.get("orden_id"))
    except (TypeError, ValueError):
        return

    # La consulta a la BD se hace en un hilo para no bloquear el resto de conexiones
    await asyncio.to_thread(
        _avisar_escribiendo, user_id, rol, orden_id, payload["tipo"] == "escribiendo"
    )


@router.websocket("/socket/orders")
async def websocket_orders(
    websocket: WebSocket,
    token: str = Query(...),
):
    user_id = None
    rol = None
    conectado = False
    try:
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            await websocket.close(code=4001)
            return

        user_id = payload.get("sub")
        rol = payload.get("role")
        jti = payload.get("jti")

        from app.core.database import SessionLocal
        from app.modules.auth.service import validate_active_session
        db = SessionLocal()
        try:
            user = get_user_by_id(db, user_id, rol)
            if not user:
                await websocket.close(code=4001)
                return
            if jti and not validate_active_session(db, user.id, rol, jti):
                await websocket.close(code=4001)
                return
            # Se guardan los valores antes de cerrar la sesión de BD
            user_id = user.id
            rol = user.rol
        finally:
            db.close()

        await manager.connect(websocket, user_id, rol)
        conectado = True

        # Keep connection alive and listen for client pings
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(), timeout=CLIENTE_TIMEOUT_SEG
                )
            except asyncio.TimeoutError:
                # El cliente dejó de dar señales: se corta y se marca desconectado
                try:
                    await websocket.close(code=4008)
                except Exception:
                    pass
                break
            except WebSocketDisconnect:
                break

            try:
                if data == "ping":
                    await websocket.send_text("pong")
                    continue
                await _procesar_mensaje_cliente(data, user_id, rol)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WS message error: {e}")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if conectado:
            manager.disconnect(websocket, user_id, rol)
