import aiofiles
from datetime import datetime
from fastapi import HTTPException, UploadFile, status
from pathlib import Path
from sqlalchemy.orm import Session
from app.modules.chat.dao import MensajeDAO
from app.modules.chat.schemas import MensajeResponse
from app.modules.service_orders.dao import OrdenServicioDAO
from app.modules.service_orders.models import Evidencia

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

    ext = Path(file.filename).suffix if file.filename else ".jpg"
    filename = f"evidencia_{orden_id}_{int(datetime.utcnow().timestamp())}{ext}"
    upload_dir = Path("uploads") / "evidencias"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename

    content = await file.read()
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    url = f"/uploads/evidencias/{filename}"

    evidencia = Evidencia(
        url=url,
        fecha=datetime.utcnow(),
        orden_servicio_id=orden_id,
        mensaje_id=mensaje_id,
    )
    db.add(evidencia)
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

    filepath = Path("uploads") / evidencia.url.lstrip("/")
    if filepath.exists():
        filepath.unlink()

    db.delete(evidencia)
    db.commit()
