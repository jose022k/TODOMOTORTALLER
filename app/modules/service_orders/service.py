import base64
import qrcode
from io import BytesIO
from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.service_orders.dao import OrdenServicioDAO
from app.modules.service_orders.schemas import (
    OrdenServicioCreate,
    OrdenServicioDetailResponse,
    OrdenServicioListResponse,
)
from app.modules.motorcycles.models import HistorialMantenimiento, MotoCliente, CatalogoMoto
from app.modules.auth.models import Admin
from app.modules.notifications.service import create_notification

orden_dao = OrdenServicioDAO()

# Transiciones de estado permitidas
TRANSICIONES_VALIDAS = {
    "pendiente": ["en_proceso", "cancelada"],
    "en_proceso": ["completada", "cancelada"],
    "completada": [],
    "cancelada": [],
}


def _build_list_response(order):
    """Construye OrdenServicioListResponse a partir de un OrdenServicio con relaciones cargadas."""
    moto = order.moto_cliente
    catalogo = moto.catalogo_moto if moto else None
    return OrdenServicioListResponse(
        id=order.id,
        descripcion=order.descripcion,
        estado=order.estado,
        fecha_creacion=order.fecha_creacion,
        fecha_cierre=order.fecha_cierre,
        cliente_id=order.cliente_id,
        cliente_nombre=order.cliente.nombre if order.cliente else "—",
        mecanico_id=order.mecanico_id,
        mecanico_nombre=order.mecanico.nombre if order.mecanico else "—",
        moto_cliente_id=order.moto_cliente_id,
        moto_placa=moto.placa if moto else "—",
        moto_anio=moto.anio if moto else None,
        moto_color_especifico=moto.color if moto else None,
        moto_marca=catalogo.marca if catalogo else "—",
        moto_modelo=catalogo.modelo if catalogo else "—",
        moto_color=catalogo.gama_color if catalogo else "—",
    )


def create_order(db: Session, data: OrdenServicioCreate, admin_user):
    """Crea una nueva orden de servicio.
    Si se proporciona catalogo_moto_id + placa + anio, registra una nueva moto
    para el cliente antes de crear la orden. De lo contrario usa moto_cliente_id existente.
    """
    moto_cliente_id = data.moto_cliente_id

    # Validar: debe venir moto_cliente_id existente O datos para nueva moto
    if not moto_cliente_id:
        if not data.catalogo_moto_id or not data.placa or not data.anio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar una moto existente (moto_cliente_id) o los datos para registrar una nueva (catalogo_moto_id, placa, anio)",
            )
        # Validar que el catálogo existe
        catalogo = db.query(CatalogoMoto).filter(CatalogoMoto.id == data.catalogo_moto_id).first()
        if not catalogo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Modelo de moto no encontrado en el catálogo",
            )
        # Crear nueva MotoCliente
        nueva_moto = MotoCliente(
            placa=data.placa.upper(),
            anio=data.anio,
            color=data.color,
            catalogo_moto_id=data.catalogo_moto_id,
            cliente_id=data.cliente_id,
        )
        db.add(nueva_moto)
        db.flush()
        moto_cliente_id = nueva_moto.id

    order_data = {
        "descripcion": data.descripcion,
        "estado": "pendiente",
        "fecha_creacion": datetime.utcnow(),
        "cliente_id": data.cliente_id,
        "mecanico_id": data.mecanico_id,
        "moto_cliente_id": moto_cliente_id,
    }
    order = orden_dao.create(db, order_data)

    # Notificar al cliente
    create_notification(db, "orden_creada", f"Se ha creado una nueva orden de servicio", orden_servicio_id=order.id, cliente_id=data.cliente_id)
    # Notificar al mecánico
    create_notification(db, "orden_creada", f"Tienes una nueva orden asignada", orden_servicio_id=order.id, mecanico_id=data.mecanico_id)
    # Notificar a todos los administradores
    admin_ids = [a.id for a in db.query(Admin.id).all()]
    for aid in admin_ids:
        create_notification(db, "orden_creada", f"Se ha creado la orden #{order.id}", orden_servicio_id=order.id, admin_id=aid)

    return order


def get_orders(
    db: Session,
    current_user,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None,
    mecanico_id: Optional[int] = None,
) -> List[OrdenServicioListResponse]:
    """Lista órdenes según el rol del usuario autenticado."""
    if current_user.rol == "mecanico":
        mecanico_id = current_user.id
        cliente_id = None
    elif current_user.rol == "cliente":
        cliente_id = current_user.id
        mecanico_id = None
    # Admin: usa los filtros pasados por query param (pueden ser None)

    orders = orden_dao.get_all_with_relations(
        db, skip=skip, limit=limit, estado=estado,
        cliente_id=cliente_id, mecanico_id=mecanico_id,
    )
    return [_build_list_response(o) for o in orders]


def count_orders(
    db: Session,
    current_user,
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None,
    mecanico_id: Optional[int] = None,
) -> int:
    if current_user.rol == "mecanico":
        mecanico_id = current_user.id
        cliente_id = None
    elif current_user.rol == "cliente":
        cliente_id = current_user.id
        mecanico_id = None

    return orden_dao.count_all_with_relations(
        db, estado=estado, cliente_id=cliente_id, mecanico_id=mecanico_id,
    )


def get_order_by_id(db: Session, order_id: int, current_user):
    """Obtiene una orden por ID con validación de acceso por rol."""
    order = orden_dao.get_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    # Validar acceso: mecanico solo ve sus órdenes, cliente solo las suyas
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

    # Cargar relaciones para la respuesta detallada
    cliente = order.cliente
    mecanico = order.mecanico
    moto_cliente = order.moto_cliente
    catalogo_moto = moto_cliente.catalogo_moto if moto_cliente else None

    return OrdenServicioDetailResponse(
        id=order.id,
        descripcion=order.descripcion,
        estado=order.estado,
        fecha_creacion=order.fecha_creacion,
        fecha_cierre=order.fecha_cierre,
        cliente_id=order.cliente_id,
        cliente_nombre=cliente.nombre if cliente else "—",
        cliente_cedula=cliente.cedula if cliente else "—",
        mecanico_id=order.mecanico_id,
        mecanico_nombre=mecanico.nombre if mecanico else "—",
        moto_cliente_id=order.moto_cliente_id,
        moto_placa=moto_cliente.placa if moto_cliente else "—",
        moto_anio=moto_cliente.anio if moto_cliente else 0,
        moto_color_especifico=moto_cliente.color if moto_cliente else None,
        moto_marca=catalogo_moto.marca if catalogo_moto else "—",
        moto_modelo=catalogo_moto.modelo if catalogo_moto else "—",
        moto_color=catalogo_moto.gama_color if catalogo_moto else "—",
    )


def update_order_status(db: Session, order_id: int, new_status: str, current_user):
    """Actualiza el estado de una orden con validación de transiciones."""
    order = orden_dao.get_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    # Validar que el mecánico solo cambie estados de sus órdenes
    if current_user.rol == "mecanico" and order.mecanico_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cambiar el estado de una orden que no te pertenece",
        )

    # Validar transición
    old_status = order.estado
    if new_status not in TRANSICIONES_VALIDAS.get(old_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cambiar el estado de '{old_status}' a '{new_status}'",
        )

    # Guardar valores necesarios antes del update
    moto_cliente_id = order.moto_cliente_id
    mecanico_id = order.mecanico_id
    descripcion = order.descripcion

    update_data = {"estado": new_status}
    if new_status == "completada":
        update_data["fecha_cierre"] = datetime.utcnow()

    updated = orden_dao.update(db, order, update_data)

    # Notificar según la transición
    admin_ids = [a.id for a in db.query(Admin.id).all()]

    if new_status == "en_proceso":
        create_notification(db, "orden_en_proceso", f"La orden #{order_id} está en proceso", orden_servicio_id=order_id, cliente_id=order.cliente_id)
        for aid in admin_ids:
            create_notification(db, "orden_en_proceso", f"La orden #{order_id} está en proceso", orden_servicio_id=order_id, admin_id=aid)
    elif new_status == "completada":
        create_notification(db, "orden_completada", f"La orden #{order_id} ha sido completada", orden_servicio_id=order_id, cliente_id=order.cliente_id)
        for aid in admin_ids:
            create_notification(db, "orden_completada", f"La orden #{order_id} ha sido completada", orden_servicio_id=order_id, admin_id=aid)
    elif new_status == "cancelada":
        create_notification(db, "orden_cancelada", f"La orden #{order_id} ha sido cancelada", orden_servicio_id=order_id, cliente_id=order.cliente_id)
        for aid in admin_ids:
            create_notification(db, "orden_cancelada", f"La orden #{order_id} ha sido cancelada", orden_servicio_id=order_id, admin_id=aid)

    # Si se completa la orden, crear historial y generar QR
    if new_status == "completada":
        _completar_orden(db, updated, moto_cliente_id, mecanico_id, descripcion)

    return updated


def _completar_orden(db: Session, order, moto_cliente_id: int, mecanico_id: int, descripcion: str):
    """Crea el historial de mantenimiento y genera el QR al completar una orden."""
    # Crear registro en historial_mantenimiento
    historial = HistorialMantenimiento(
        descripcion=descripcion,
        fecha=datetime.utcnow(),
        moto_cliente_id=moto_cliente_id,
        orden_servicio_id=order.id,
        mecanico_id=mecanico_id,
    )
    db.add(historial)

    # Generar QR con la URL del tracker
    from app.core.config import FRONTEND_URL
    qr_data = f"{FRONTEND_URL}/tracker/moto/{moto_cliente_id}"
    qr_img = qrcode.make(qr_data)
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    codigo_qr = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

    # Actualizar QR en la moto del cliente
    moto_cliente = db.query(MotoCliente).filter(MotoCliente.id == moto_cliente_id).first()
    if moto_cliente:
        moto_cliente.codigo_qr = codigo_qr

    db.commit()


def assign_mechanic(db: Session, order_id: int, mecanico_id: int, admin_user):
    """Reasigna un mecánico a una orden existente. Solo administradores."""
    order = orden_dao.get_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )

    # No permitir reasignar si la orden ya está completada o cancelada
    if order.estado in ("completada", "cancelada"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede reasignar mecánico en una orden '{order.estado}'",
        )

    return orden_dao.update(db, order, {"mecanico_id": mecanico_id})


def get_order_tracker(db: Session, order_id: int):
    order = orden_dao.get_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de servicio no encontrada",
        )
    return {
        "id": order.id,
        "estado": order.estado,
        "descripcion": order.descripcion,
        "fecha_creacion": order.fecha_creacion,
        "fecha_cierre": order.fecha_cierre,
        "cliente_nombre": order.cliente.nombre if order.cliente else "—",
        "mecanico_nombre": order.mecanico.nombre if order.mecanico else "—",
        "moto_marca": order.moto_cliente.catalogo_moto.marca if order.moto_cliente and order.moto_cliente.catalogo_moto else "—",
        "moto_modelo": order.moto_cliente.catalogo_moto.modelo if order.moto_cliente and order.moto_cliente.catalogo_moto else "—",
        "moto_placa": order.moto_cliente.placa if order.moto_cliente else "—",
        "moto_cliente_id": order.moto_cliente_id,
    }


def get_moto_history(db: Session, moto_cliente_id: int):
    orders = orden_dao.get_all_with_relations(
        db, skip=0, limit=500, moto_cliente_id=moto_cliente_id
    )
    return [_build_list_response(o) for o in orders]
