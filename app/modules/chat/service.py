import cloudinary
import cloudinary.uploader
from datetime import datetime
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
from app.modules.chat.dao import MensajeDAO
from app.modules.chat.schemas import MensajeResponse
from app.modules.service_orders.dao import OrdenServicioDAO
from app.modules.service_orders.models import Evidencia
from app.modules.auth.models import Admin
from app.modules.notifications.service import create_notification

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

    # Notificar a los otros participantes de la orden (excluyendo al remitente)
    sender_role = current_user.rol
    if sender_role == "admin":
        if order.cliente_id:
            create_notification(db, "mensaje_recibido", f"Nuevo mensaje en la orden #{orden_id}", orden_servicio_id=orden_id, cliente_id=order.cliente_id, open_chat=True)
        if order.mecanico_id:
            create_notification(db, "mensaje_recibido", f"Nuevo mensaje en la orden #{orden_id}", orden_servicio_id=orden_id, mecanico_id=order.mecanico_id, open_chat=True)
    elif sender_role == "mecanico":
        if order.cliente_id:
            create_notification(db, "mensaje_recibido", f"Nuevo mensaje en la orden #{orden_id}", orden_servicio_id=orden_id, cliente_id=order.cliente_id, open_chat=True)
        for aid in [a.id for a in db.query(Admin.id).all()]:
            if aid != user_id:
                create_notification(db, "mensaje_recibido", f"Nuevo mensaje en la orden #{orden_id}", orden_servicio_id=orden_id, admin_id=aid, open_chat=True)
    elif sender_role == "cliente":
        if order.mecanico_id:
            create_notification(db, "mensaje_recibido", f"Nuevo mensaje en la orden #{orden_id}", orden_servicio_id=orden_id, mecanico_id=order.mecanico_id, open_chat=True)
        for aid in [a.id for a in db.query(Admin.id).all()]:
            if aid != user_id:
                create_notification(db, "mensaje_recibido", f"Nuevo mensaje en la orden #{orden_id}", orden_servicio_id=orden_id, admin_id=aid, open_chat=True)

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


def create_evidencia(db: Session, orden_id: int, file: UploadFile, mensaje_id, current_user):
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

    result = cloudinary.uploader.upload(
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

    # Notificar a los participantes de la orden (excluyendo al remitente)
    if order.cliente_id and order.cliente_id != current_user.id:
        create_notification(db, "evidencia_enviada", f"Nueva evidencia en la orden #{orden_id}", orden_servicio_id=orden_id, cliente_id=order.cliente_id, open_chat=True)
    if order.mecanico_id and order.mecanico_id != current_user.id:
        create_notification(db, "evidencia_enviada", f"Nueva evidencia en la orden #{orden_id}", orden_servicio_id=orden_id, mecanico_id=order.mecanico_id, open_chat=True)
    for aid in [a.id for a in db.query(Admin.id).all()]:
        if aid != current_user.id:
            create_notification(db, "evidencia_enviada", f"Nueva evidencia en la orden #{orden_id}", orden_servicio_id=orden_id, admin_id=aid, open_chat=True)

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
        cloudinary.uploader.destroy(full_public_id)

    db.delete(evidencia)
    db.commit()
