import base64
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.service_orders.dao import OrdenServicioDAO
from app.modules.service_orders.models import OrdenServicio
from app.modules.service_orders.schemas import (
    OrdenServicioCreate,
    OrdenServicioDetailResponse,
    OrdenServicioListResponse,
)
from app.modules.motorcycles.models import HistorialMantenimiento, MotoCliente, CatalogoMoto
from app.modules.auth.models import Admin
from app.modules.notifications.service import create_notifications_in_background
from app.modules.bcv.service import convertir_a_usd
from app.core.ws_manager import manager

orden_dao = OrdenServicioDAO()

# Transiciones de estado permitidas
TRANSICIONES_VALIDAS = {
    "pendiente": ["en_proceso", "cancelada"],
    "en_proceso": ["completada", "cancelada"],
    "completada": [],
    "cancelada": [],
}

# Monto máximo de una orden, expresado en euros (USD)
MAX_MONTO_EUR = 1500.0
# Ventana (segundos) en la que se considera "doble envío" una orden idéntica
DUPLICADOS_VENTANA_SEG = 60


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
        monto=order.monto,
        moneda=order.moneda,
        tasa_bcv=order.tasa_bcv,
        monto_usd=order.monto_usd,
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

    Protecciones aplicadas:
      · Máximo de monto (MAX_MONTO_EUR en €, o su equivalente en Bs con la tasa BCV).
      · No se permite una segunda orden activa (pendiente/en proceso) para la misma moto.
      · No se permite enviar dos veces la misma orden (doble clic / reenvío).
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
        # Si el cliente ya tiene una moto con esa placa, se reutiliza el registro
        # en lugar de crear uno duplicado (una placa identifica a una sola moto).
        moto_con_placa = (
            db.query(MotoCliente)
            .filter(
                MotoCliente.cliente_id == data.cliente_id,
                MotoCliente.placa == data.placa.upper(),
            )
            .first()
        )
        if moto_con_placa:
            moto_cliente_id = moto_con_placa.id
        else:
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
    else:
        # Validar que la moto exista y pertenezca al cliente indicado
        moto = db.query(MotoCliente).filter(MotoCliente.id == moto_cliente_id).first()
        if not moto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Moto del cliente no encontrada",
            )
        if moto.cliente_id != data.cliente_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La moto seleccionada no pertenece al cliente indicado",
            )
        moto_cliente_id = moto.id

    # ── Protección 1: una sola orden activa por moto ──
    orden_activa = (
        db.query(OrdenServicio.id)
        .filter(
            OrdenServicio.moto_cliente_id == moto_cliente_id,
            OrdenServicio.estado.in_(("pendiente", "en_proceso")),
        )
        .first()
    )
    if orden_activa:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Esta moto ya tiene una orden activa (#{orden_activa[0]}). "
                "Cancele o complétela antes de crear otra."
            ),
        )

    # ── Protección 2: misma orden enviada dos veces en poco tiempo ──
    desde = datetime.utcnow() - timedelta(seconds=DUPLICADOS_VENTANA_SEG)
    duplicada = (
        db.query(OrdenServicio.id)
        .filter(
            OrdenServicio.cliente_id == data.cliente_id,
            OrdenServicio.moto_cliente_id == moto_cliente_id,
            OrdenServicio.descripcion == data.descripcion,
            OrdenServicio.monto == data.monto,
            OrdenServicio.moneda == data.moneda,
            OrdenServicio.fecha_creacion >= desde,
        )
        .first()
    )
    if duplicada:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Orden duplicada: esta orden ya fue registrada hace unos segundos.",
        )

    order_data = {
        "descripcion": data.descripcion,
        "estado": "pendiente",
        "fecha_creacion": datetime.utcnow(),
        "cliente_id": data.cliente_id,
        "mecanico_id": data.mecanico_id,
        "moto_cliente_id": moto_cliente_id,
        "monto": data.monto,
        "moneda": data.moneda,
    }

    # Convertir a USD según la moneda (Bs usa la tasa BCV)
    try:
        monto_usd, tasa, _ = convertir_a_usd(db, data.monto, data.moneda)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # ── Límite de monto: tope en euros (o su equivalente en Bs) ──
    if monto_usd > MAX_MONTO_EUR:
        if data.moneda == "BS" and tasa:
            equivalencia = f"{MAX_MONTO_EUR * tasa:,.2f} Bs".replace(",", ".")
            detalle = f"El monto no puede superar €{MAX_MONTO_EUR:,.0f} (equivalente a {equivalencia} según la tasa BCV)."
        else:
            detalle = f"El monto no puede superar €{MAX_MONTO_EUR:,.0f}."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detalle,
        )

    order_data["monto_usd"] = monto_usd
    order_data["tasa_bcv"] = tasa

    order = orden_dao.create(db, order_data)

    # Ids de administradores: se necesitan también para el broadcast
    admin_ids = [a.id for a in db.query(Admin.id).all()]

    # Las notificaciones se crean en segundo plano (la respuesta no espera)
    create_notifications_in_background([
        {
            "tipo": "orden_creada",
            "mensaje": "Se ha creado una nueva orden de servicio",
            "orden_servicio_id": order.id,
            "cliente_id": data.cliente_id,
        },
        {
            "tipo": "orden_creada",
            "mensaje": "Tienes una nueva orden asignada",
            "orden_servicio_id": order.id,
            "mecanico_id": data.mecanico_id,
        },
        *[
            {
                "tipo": "orden_creada",
                "mensaje": f"Se ha creado la orden #{order.id}",
                "orden_servicio_id": order.id,
                "admin_id": aid,
            }
            for aid in admin_ids
        ],
    ])

    # Broadcast WebSocket
    manager.schedule_broadcast_order_event(
        "orden_creada", order.id, "pendiente",
        cliente_id=data.cliente_id, mecanico_id=data.mecanico_id,
        admin_ids=admin_ids,
    )

    return order


def get_orders(
    db: Session,
    current_user,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None,
    mecanico_id: Optional[int] = None,
    q: Optional[str] = None,
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
        cliente_id=cliente_id, mecanico_id=mecanico_id, q=q,
    )
    return [_build_list_response(o) for o in orders]


def count_orders(
    db: Session,
    current_user,
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None,
    mecanico_id: Optional[int] = None,
    q: Optional[str] = None,
) -> int:
    if current_user.rol == "mecanico":
        mecanico_id = current_user.id
        cliente_id = None
    elif current_user.rol == "cliente":
        cliente_id = current_user.id
        mecanico_id = None

    return orden_dao.count_all_with_relations(
        db, estado=estado, cliente_id=cliente_id, mecanico_id=mecanico_id, q=q,
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
        monto=order.monto,
        moneda=order.moneda,
        tasa_bcv=order.tasa_bcv,
        monto_usd=order.monto_usd,
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

    # Ids de administradores: se necesitan también para el broadcast
    admin_ids = [a.id for a in db.query(Admin.id).all()]

    # Las notificaciones se crean en segundo plano (la respuesta no espera)
    if new_status == "en_proceso":
        mensaje = f"La orden #{order_id} está en proceso"
        specs = [{"tipo": "orden_en_proceso", "mensaje": mensaje, "orden_servicio_id": order_id, "cliente_id": order.cliente_id}]
        if order.mecanico_id:
            specs.append({"tipo": "orden_en_proceso", "mensaje": mensaje, "orden_servicio_id": order_id, "mecanico_id": order.mecanico_id})
    elif new_status == "completada":
        mensaje = f"La orden #{order_id} ha sido completada"
        specs = [{"tipo": "orden_completada", "mensaje": mensaje, "orden_servicio_id": order_id, "cliente_id": order.cliente_id}]
    else:  # cancelada
        mensaje = f"La orden #{order_id} ha sido cancelada"
        specs = [{"tipo": "orden_cancelada", "mensaje": mensaje, "orden_servicio_id": order_id, "cliente_id": order.cliente_id}]
        if order.mecanico_id:
            specs.append({"tipo": "orden_cancelada", "mensaje": mensaje, "orden_servicio_id": order_id, "mecanico_id": order.mecanico_id})

    specs.extend(
        {"tipo": f"orden_{new_status}", "mensaje": mensaje, "orden_servicio_id": order_id, "admin_id": aid}
        for aid in admin_ids
    )
    create_notifications_in_background(specs)

    # Si se completa la orden, crear historial y generar QR
    if new_status == "completada":
        _completar_orden(db, updated, moto_cliente_id, mecanico_id, descripcion)

    # Broadcast WebSocket
    manager.schedule_broadcast_order_event(
        "orden_actualizada", order_id, new_status,
        cliente_id=order.cliente_id, mecanico_id=order.mecanico_id,
        admin_ids=admin_ids,
    )

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

    old_mecanico_id = order.mecanico_id
    updated = orden_dao.update(db, order, {"mecanico_id": mecanico_id})

    # Ids de administradores: se necesitan también para el broadcast
    admin_ids = [a.id for a in db.query(Admin.id).all()]

    # Notificaciones en segundo plano (la respuesta no espera)
    create_notifications_in_background([
        *(
            [{"tipo": "orden_actualizada", "mensaje": f"Has sido desasignado de la orden #{order_id}",
              "orden_servicio_id": order_id, "mecanico_id": old_mecanico_id}]
            if old_mecanico_id and old_mecanico_id != mecanico_id else []
        ),
        *(
            [{"tipo": "orden_actualizada", "mensaje": f"La orden #{order_id} tiene un nuevo mecánico asignado",
              "orden_servicio_id": order_id, "cliente_id": updated.cliente_id}]
            if updated.cliente_id else []
        ),
        {"tipo": "orden_actualizada", "mensaje": f"Te han asignado la orden #{order_id}",
         "orden_servicio_id": order_id, "mecanico_id": mecanico_id},
        *[
            {"tipo": "orden_actualizada", "mensaje": f"Se reasignó mecánico en la orden #{order_id}",
             "orden_servicio_id": order_id, "admin_id": aid}
            for aid in admin_ids
        ],
    ])

    # Broadcast WebSocket
    manager.schedule_broadcast_order_event(
        "orden_actualizada", order_id, updated.estado,
        cliente_id=updated.cliente_id, mecanico_id=mecanico_id,
        admin_ids=admin_ids,
    )

    return updated


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
