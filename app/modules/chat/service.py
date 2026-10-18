import asyncio
import cloudinary
import cloudinary.uploader
import threading
from datetime import datetime
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
from app.modules.chat.dao import MensajeDAO
from app.modules.chat.schemas import MensajeResponse
from app.modules.service_orders.dao import OrdenServicioDAO
from app.modules.service_orders.models import Evidencia
from app.modules.auth.models import Admin
from app.modules.notifications.service import create_notifications_in_background

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

mensaje_dao = MensajeDAO()
orden_dao = OrdenServicioDAO()


def _build_mensaje_response(m) -> MensajeResponse:
    if m.admin_id:
        remitente_id = m.admin.id
        remitente_nombre = m.admin.nombre
        remitente_rol = "admin"
    elif m.mecanico_id:
        remitente_id = m.mecanico.id
        remitente_nombre = m.mecanico.nombre
        remitente_rol = "mecanico"
    elif m.cliente_id:
        remitente_id = m.cliente.id
        remitente_nombre = m.cliente.nombre
        remitente_rol = "cliente"
    else:
        remitente_id = 0
        remitente_nombre = "Desconocido"
        remitente_rol = "desconocido"

    return MensajeResponse(
        id=m.id,
        contenido=m.contenido,
        fecha_hora=m.fecha_hora,
        editado=m.editado or False,
        fecha_edicion=m.fecha_edicion,
        orden_servicio_id=m.orden_servicio_id,
        remitente_id=remitente_id,
        remitente_nombre=remitente_nombre,
        remitente_rol=remitente_rol,
    )


def _validar_acceso_orden(order, current_user):
    if current_user.rol == "mecanico" and order.mecanico_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta orden",
        )
    if current_user.rol == "cliente" and order.cliente_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta orden",
        )


def _ids_admins(db: Session):
    return [a.id for a in db.query(Admin.id).all()]


def _notificar_participantes_chat(db: Session, order, tipo: str, titulo_mensaje: str, current_user, texto_detalle: str = None):
    """Prepara las notificaciones del chat y las crea EN SEGUNDO PLANO.

    Así enviar un mensaje o una evidencia responde de inmediato: no se espera
    a escribir en la base de datos ni a enviar los pushes de cada participante.
    """
    orden_id = order.id
    sender_role = current_user.rol
    sender_id = current_user.id
    sender_name = getattr(current_user, "nombre", "Usuario")

    if texto_detalle:
        msg_text = f"{sender_name}: {texto_detalle}"
    else:
        msg_text = f"{titulo_mensaje} en la orden #{orden_id}"

    specs = []

    # Notificar al cliente de la orden (si no es el remitente)
    if order.cliente_id and not (sender_role == "cliente" and order.cliente_id == sender_id):
        specs.append({"tipo": tipo, "mensaje": msg_text, "orden_servicio_id": orden_id,
                      "cliente_id": order.cliente_id, "open_chat": True})

    # Notificar al mecánico de la orden (si no es el remitente)
    if order.mecanico_id and not (sender_role == "mecanico" and order.mecanico_id == sender_id):
        specs.append({"tipo": tipo, "mensaje": msg_text, "orden_servicio_id": orden_id,
                      "mecanico_id": order.mecanico_id, "open_chat": True})

    # Notificar a los administradores (excluyendo al remitente si es un admin)
    for aid in _ids_admins(db):
        if not (sender_role == "admin" and aid == sender_id):
            specs.append({"tipo": tipo, "mensaje": msg_text, "orden_servicio_id": orden_id,
                          "admin_id": aid, "open_chat": True})

    create_notifications_in_background(specs)


def _avisar_chat(db: Session, order):
    """Avisa por WebSocket a los participantes que el chat cambió.

    Permite que el chat de la otra persona se actualice AL INSTANTE,
    sin esperar al sondeo de 2 segundos.
    """
    try:
        if not order:
            return
        from app.core.ws_manager import manager
        manager.schedule_broadcast_chat(
            order.id, order.cliente_id, order.mecanico_id, _ids_admins(db),
        )
    except Exception:
        pass


def send_message(db: Session, orden_id: int, contenido: str, current_user):
    order = orden_dao.get_by_id(db, orden_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    _validar_acceso_orden(order, current_user)

    if order.estado != "en_proceso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden enviar mensajes en órdenes en proceso",
        )

    user_id = current_user.id
    remitente_field = {
        "admin": "admin_id",
        "mecanico": "mecanico_id",
        "cliente": "cliente_id",
    }.get(current_user.rol)

    msg_data = {
        "contenido": contenido,
        "fecha_hora": datetime.utcnow(),
        "orden_servicio_id": orden_id,
        remitente_field: user_id,
    }

    msg = mensaje_dao.create(db, msg_data)

    # Notificar a los destinatarios con el texto del mensaje enviado
    _notificar_participantes_chat(db, order, "mensaje_recibido", "Nuevo mensaje", current_user, texto_detalle=contenido)
    # Avisa al chat de los demás para que se actualice al instante
    _avisar_chat(db, order)

    return _build_mensaje_response(msg)


def edit_message(db: Session, orden_id: int, mensaje_id: int, contenido: str, current_user):
    msg = mensaje_dao.get_by_id(db, mensaje_id)
    if not msg or msg.orden_servicio_id != orden_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado",
        )

    remitente_field = {
        "admin": "admin_id",
        "mecanico": "mecanico_id",
        "cliente": "cliente_id",
    }.get(current_user.rol)

    sender_id = getattr(msg, remitente_field, None) if remitente_field else None
    if sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes editar mensajes de otros usuarios",
        )

    delta = datetime.utcnow() - msg.fecha_hora
    if delta.total_seconds() > 600:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes editar mensajes dentro de los primeros 10 minutos",
        )

    msg.contenido = contenido
    msg.editado = True
    msg.fecha_edicion = datetime.utcnow()
    db.commit()
    db.refresh(msg)
    _avisar_chat(db, orden_dao.get_by_id(db, orden_id))
    return _build_mensaje_response(msg)


def get_messages(db: Session, orden_id: int, current_user):
    order = orden_dao.get_by_id(db, orden_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    _validar_acceso_orden(order, current_user)

    if order.estado != "en_proceso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los mensajes solo están disponibles mientras la orden está en proceso",
        )

    mensajes = mensaje_dao.get_by_orden(db, orden_id)
    return [_build_mensaje_response(m) for m in mensajes]


def get_evidencias(db: Session, orden_id: int, current_user):
    order = orden_dao.get_by_id(db, orden_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    _validar_acceso_orden(order, current_user)

    if order.estado != "en_proceso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las evidencias solo están disponibles mientras la orden está en proceso",
        )

    evidencias = (
        db.query(Evidencia)
        .filter(Evidencia.orden_servicio_id == orden_id)
        .order_by(Evidencia.fecha.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "url": e.url,
            "fecha": e.fecha,
            "orden_servicio_id": e.orden_servicio_id,
            "mensaje_id": e.mensaje_id,
        }
        for e in evidencias
    ]


async def create_evidencia(db: Session, orden_id: int, file: UploadFile, mensaje_id, current_user):
    order = orden_dao.get_by_id(db, orden_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    _validar_acceso_orden(order, current_user)

    if order.estado != "en_proceso":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden agregar evidencias en órdenes en proceso",
        )

    # La subida a Cloudinary es de red: se hace en un hilo para no bloquear
    # el resto de peticiones del sistema mientras se sube la evidencia.
    result = await asyncio.to_thread(
        cloudinary.uploader.upload,
        file.file,
        folder="evidencias",
        public_id=f"evidencia_{orden_id}_{int(datetime.utcnow().timestamp())}",
    )

    evidencia = Evidencia(
        url=result["secure_url"],
        fecha=datetime.utcnow(),
        orden_servicio_id=orden_id,
        mensaje_id=mensaje_id,
    )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)

    # Notificar a los destinatarios con el texto de evidencia enviado
    _notificar_participantes_chat(db, order, "evidencia_enviada", "Nueva evidencia", current_user, texto_detalle="Envió una evidencia adjunta")
    _avisar_chat(db, order)

    return evidencia


def link_evidencia(db: Session, orden_id: int, evidencia_id: int, mensaje_id: int, current_user):
    order = orden_dao.get_by_id(db, orden_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    _validar_acceso_orden(order, current_user)
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id, Evidencia.orden_servicio_id == orden_id).first()
    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    evidencia.mensaje_id = mensaje_id
    db.commit()
    db.refresh(evidencia)
    _avisar_chat(db, order)
    return evidencia


def delete_evidencia(db: Session, orden_id: int, evidencia_id: int, current_user):
    order = orden_dao.get_by_id(db, orden_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    _validar_acceso_orden(order, current_user)

    evidencia = db.query(Evidencia).filter(
        Evidencia.id == evidencia_id,
        Evidencia.orden_servicio_id == orden_id,
    ).first()
    if not evidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidencia no encontrada",
        )

    if "cloudinary" in evidencia.url:
        public_id = evidencia.url.split("/v")[1].split(".")[0]
        full_public_id = f"evidencias/{public_id.split('/')[-1]}"
        # Se borra en un hilo para no esperar a la respuesta de Cloudinary
        threading.Thread(
            target=cloudinary.uploader.destroy,
            args=(full_public_id,),
            daemon=True,
        ).start()

    db.delete(evidencia)
    db.commit()
    _avisar_chat(db, order)


def get_presencia(db: Session, orden_id: int, current_user):
    """Quién está conectado («En línea») en el chat de esta orden."""
    from app.modules.auth.service import get_user_by_id
    from app.core.ws_manager import manager

    order = orden_dao.get_by_id(db, orden_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    _validar_acceso_orden(order, current_user)

    def _persona(user_id, rol):
        if not user_id:
            return None
        user = get_user_by_id(db, user_id, rol)
        if not user:
            return None
        return {
            "id": user.id,
            "nombre": getattr(user, "nombre", ""),
            "rol": rol,
            "online": manager.is_online(user.id, rol),
        }

    return {
        "cliente": _persona(order.cliente_id, "cliente"),
        "mecanico": _persona(order.mecanico_id, "mecanico"),
        "admins": [
            {
                "id": a.id,
                "nombre": a.nombre,
                "rol": "admin",
                "online": manager.is_online(a.id, "admin"),
            }
            for a in db.query(Admin).all()
        ],
    }
