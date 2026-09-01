from datetime import datetime, timedelta, time
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.modules.auth.dao import ClienteDAO, MecanicoDAO
from app.modules.auth.models import Cliente
from app.modules.service_orders.models import OrdenServicio
from app.modules.motorcycles.models import MotoCliente, CatalogoMoto

cliente_dao = ClienteDAO()
mecanico_dao = MecanicoDAO()


def get_dashboard(db: Session) -> dict:
    clientes = cliente_dao.get_all(db)
    mecanicos = mecanico_dao.get_all(db)
    ordenes = db.query(OrdenServicio).all()

    total_ordenes_pendientes = sum(1 for o in ordenes if o.estado == "pendiente")
    total_ordenes_en_proceso = sum(1 for o in ordenes if o.estado == "en_proceso")
    total_ordenes_completadas = sum(1 for o in ordenes if o.estado == "completada")
    total_ordenes_canceladas = sum(1 for o in ordenes if o.estado == "cancelada")

    return {
        "total_clientes": len(clientes),
        "total_clientes_activos": sum(1 for c in clientes if c.activo),
        "total_mecanicos": len(mecanicos),
        "total_mecanicos_activos": sum(1 for m in mecanicos if m.activo),
        "total_ordenes_pendientes": total_ordenes_pendientes,
        "total_ordenes_en_proceso": total_ordenes_en_proceso,
        "total_ordenes_completadas": total_ordenes_completadas,
        "total_ordenes_canceladas": total_ordenes_canceladas,
    }


def get_daily_stats(db: Session) -> dict:
    hoy = datetime.combine(datetime.utcnow().date(), time.min)

    ordenes_hoy = (
        db.query(OrdenServicio)
        .filter(OrdenServicio.fecha_creacion >= hoy)
        .all()
    )

    cliente_ids_hoy = set()
    moto_ids_hoy = set()
    descripciones = []
    marcas = []

    for o in ordenes_hoy:
        cliente_ids_hoy.add(o.cliente_id)
        moto_ids_hoy.add(o.moto_cliente_id)
        if o.descripcion:
            descripciones.append(o.descripcion.strip())

    clientes_nuevos_hoy = 0
    for cid in cliente_ids_hoy:
        primera_orden = (
            db.query(OrdenServicio)
            .filter(OrdenServicio.cliente_id == cid)
            .order_by(OrdenServicio.fecha_creacion.asc())
            .first()
        )
        if primera_orden and primera_orden.fecha_creacion >= hoy:
            clientes_nuevos_hoy += 1

    if moto_ids_hoy:
        motos = (
            db.query(CatalogoMoto.marca)
            .join(MotoCliente, MotoCliente.catalogo_moto_id == CatalogoMoto.id)
            .filter(MotoCliente.id.in_(moto_ids_hoy))
            .all()
        )
        marcas = [m[0] for m in motos if m[0]]

    servicio_mas = ""
    if descripciones:
        from collections import Counter
        conteo = Counter(descripciones)
        servicio_mas = conteo.most_common(1)[0][0]

    marca_mas = ""
    if marcas:
        from collections import Counter
        conteo = Counter(marcas)
        marca_mas = conteo.most_common(1)[0][0]

    top_modelos_raw = (
        db.query(
            CatalogoMoto.marca,
            CatalogoMoto.modelo,
            func.count(OrdenServicio.id).label("total")
        )
        .join(MotoCliente, MotoCliente.catalogo_moto_id == CatalogoMoto.id)
        .join(OrdenServicio, OrdenServicio.moto_cliente_id == MotoCliente.id)
        .group_by(CatalogoMoto.id, CatalogoMoto.marca, CatalogoMoto.modelo)
        .order_by(func.count(OrdenServicio.id).desc())
        .limit(3)
        .all()
    )

    top_3_list = []
    for idx, item in enumerate(top_modelos_raw, 1):
        marca_nom = item.marca or ""
        modelo_nom = item.modelo or ""
        nombre_completo = f"{marca_nom} {modelo_nom}".strip()
        top_3_list.append(f"{idx}: {nombre_completo}")

    top_3_str = ", ".join(top_3_list) if top_3_list else "Sin datos"

    return {
        "clientes_registrados_hoy": len(cliente_ids_hoy),
        "motos_atendidas_hoy": len(moto_ids_hoy),
        "clientes_nuevos_hoy": clientes_nuevos_hoy,
        "servicio_mas_realizado_hoy": servicio_mas or "Sin datos",
        "marca_mas_atendida_hoy": marca_mas or "Sin datos",
        "top_3_modelos": top_3_str,
    }
