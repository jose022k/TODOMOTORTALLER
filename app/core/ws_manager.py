import asyncio
from fastapi import WebSocket
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

_main_loop: Optional[asyncio.AbstractEventLoop] = None


def init_ws():
    global _main_loop
    _main_loop = asyncio.get_running_loop()
    logger.info("WebSocket manager initialized")


def _run_async(coro):
    if _main_loop is None:
        logger.error("WebSocket manager not initialized")
        return
    try:
        asyncio.run_coroutine_threadsafe(coro, _main_loop)
    except Exception as e:
        logger.error(f"WebSocket _run_async FAILED: {e}")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    def _user_key(self, user_id: int, role: str) -> str:
        return f"{user_id}_{role}"

    def is_online(self, user_id: int, role: str) -> bool:
        """True si el usuario tiene al menos una pestaña conectada."""
        return bool(self.active_connections.get(self._user_key(user_id, role)))

    def _all_targets(self):
        """Todos los (user_id, rol) conectados ahora mismo."""
        targets = []
        for key in list(self.active_connections.keys()):
            uid, _, role = key.rpartition("_")
            try:
                targets.append((int(uid), role))
            except ValueError:
                continue
        return targets

    async def connect(self, websocket: WebSocket, user_id: int, role: str):
        await websocket.accept()
        key = self._user_key(user_id, role)
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)
        logger.debug(f"WS connected: {key}")
        # Avisa a todos que este usuario acaba de conectarse (indicador "En línea")
        self.schedule_broadcast_presence(user_id, role, True)

    def disconnect(self, websocket: WebSocket, user_id: int, role: str):
        key = self._user_key(user_id, role)
        quedo_conectado = False
        if key in self.active_connections:
            self.active_connections[key] = [ws for ws in self.active_connections[key] if ws != websocket]
            if not self.active_connections[key]:
                del self.active_connections[key]
            else:
                quedo_conectado = True
        logger.info(f"WebSocket disconnected: {key}")
        # Solo se marca "desconectado" si ya no queda ninguna pestaña abierta
        if not quedo_conectado:
            uid, _, role = key.rpartition("_")
            try:
                self.schedule_broadcast_presence(int(uid), role, False)
            except ValueError:
                pass

    async def broadcast_to_users(self, message: dict, user_ids: List[tuple]):
        sent = 0
        for user_id, role in user_ids:
            key = self._user_key(user_id, role)
            if key not in self.active_connections:
                continue
            for ws in self.active_connections[key][:]:
                try:
                    await ws.send_json(message)
                    sent += 1
                except Exception:
                    self.disconnect(ws, user_id, role)
        logger.debug(f"WS broadcast tipo={message.get('tipo')} sent={sent} targets={len(user_ids)}")

    async def broadcast_order_event(self, event_type: str, order_id: int, estado: str, cliente_id: int, mecanico_id: int, admin_ids: List[int]):
        payload = {
            "tipo": event_type,
            "order_id": order_id,
            "estado": estado,
        }
        targets = [(cliente_id, "cliente"), (mecanico_id, "mecanico")]
        targets.extend((aid, "admin") for aid in admin_ids)
        await self.broadcast_to_users(payload, targets)

    def schedule_broadcast_order_event(self, event_type: str, order_id: int, estado: str, cliente_id: int, mecanico_id: int, admin_ids: List[int]):
        _run_async(self.broadcast_order_event(
            event_type, order_id, estado,
            cliente_id, mecanico_id, admin_ids,
        ))

    def schedule_broadcast_notification(self, notificacion: dict, targets: List[tuple]):
        _run_async(self.broadcast_to_users(
            {"tipo": "notificacion_creada", "notificacion": notificacion},
            targets,
        ))

    def schedule_broadcast_chat(self, orden_id: int, cliente_id, mecanico_id, admin_ids: List[int]):
        """Avisa a los participantes de la orden que el chat cambió.

        El front solo recarga el chat de esa orden (nunca la lista de órdenes),
        y lo hace al instante en lugar de esperar al sondeo.
        """
        targets = []
        if cliente_id:
            targets.append((cliente_id, "cliente"))
        if mecanico_id:
            targets.append((mecanico_id, "mecanico"))
        targets.extend((aid, "admin") for aid in (admin_ids or []))
        if not targets:
            return
        _run_async(self.broadcast_to_users(
            {"tipo": "chat_actualizado", "orden_id": orden_id},
            targets,
        ))

    def schedule_broadcast_presence(self, user_id: int, role: str, online: bool):
        """Indicador de "En línea" del chat."""
        targets = self._all_targets()
        if not targets:
            return
        _run_async(self.broadcast_to_users(
            {"tipo": "presencia", "user_id": user_id, "rol": role, "online": online},
            targets,
        ))

    def schedule_broadcast_typing(self, orden_id: int, targets: List[tuple], user_id: int, role: str, escribiendo: bool):
        """Avisa a los demás participantes de la orden que alguien está escribiendo."""
        if not targets:
            return
        _run_async(self.broadcast_to_users(
            {
                "tipo": "escribiendo" if escribiendo else "dejo_de_escribir",
                "orden_id": orden_id,
                "user_id": user_id,
                "rol": role,
            },
            targets,
        ))


manager = ConnectionManager()
