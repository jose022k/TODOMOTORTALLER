from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.service_orders.models import OrdenServicio
from app.modules.motorcycles.models import MotoCliente, CatalogoMoto
from app.modules.auth.models import Cliente, Mecanico


def _to_dict(row, keys):
    return dict(zip(keys, row))


def _apply_date_filter(query, model, fecha_inicio=None, fecha_fin=None):
    if fecha_inicio:
        query = query.filter(model.fecha_creacion >= fecha_inicio)
    if fecha_fin:
        query = query.filter(model.fecha_creacion <= fecha_fin)
    return query


def get_mecanico_mas_servicios(db: Session, limite: int = 5, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    q = (
        db.query(
            Mecanico.id,
            Mecanico.nombre,
            func.count(OrdenServicio.id).label("total_servicios"),
        )
        .join(OrdenServicio, OrdenServicio.mecanico_id == Mecanico.id)
        .filter(OrdenServicio.estado == "completada")
    )
    q = _apply_date_filter(q, OrdenServicio, fecha_inicio, fecha_fin)
    rows = q.group_by(Mecanico.id).order_by(func.count(OrdenServicio.id).desc()).limit(limite).all()
    return [_to_dict(r, ["id", "nombre", "total_servicios"]) for r in rows]


def get_motos_mas_atendidas(db: Session, limite: int = 5, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    q = (
        db.query(
            CatalogoMoto.marca,
            CatalogoMoto.modelo,
            func.count(OrdenServicio.id).label("total_ordenes"),
        )
        .select_from(CatalogoMoto)
        .join(MotoCliente, MotoCliente.catalogo_moto_id == CatalogoMoto.id)
        .join(OrdenServicio, OrdenServicio.moto_cliente_id == MotoCliente.id)
        .filter(OrdenServicio.estado == "completada")
    )
    q = _apply_date_filter(q, OrdenServicio, fecha_inicio, fecha_fin)
    rows = q.group_by(CatalogoMoto.id).order_by(func.count(OrdenServicio.id).desc()).limit(limite).all()
    return [_to_dict(r, ["marca", "modelo", "total_ordenes"]) for r in rows]


def get_clientes_recurrentes(db: Session, limite: int = 5, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    q = (
        db.query(
            Cliente.id,
            Cliente.nombre,
            Cliente.cedula,
            func.count(OrdenServicio.id).label("total_ordenes"),
        )
        .join(OrdenServicio, OrdenServicio.cliente_id == Cliente.id)
    )
    q = _apply_date_filter(q, OrdenServicio, fecha_inicio, fecha_fin)
    rows = q.group_by(Cliente.id).order_by(func.count(OrdenServicio.id).desc()).limit(limite).all()
    return [_to_dict(r, ["id", "nombre", "cedula", "total_ordenes"]) for r in rows]


def get_tiempo_promedio_reparacion(db: Session, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    q = db.query(
        func.avg(
            func.extract("epoch", OrdenServicio.fecha_cierre - OrdenServicio.fecha_creacion)
            / 60
        ).label("minutos_promedio")
    ).filter(
        OrdenServicio.estado == "completada",
        OrdenServicio.fecha_cierre.isnot(None),
    )
    q = _apply_date_filter(q, OrdenServicio, fecha_inicio, fecha_fin)
    result = q.scalar()
    return {"minutos_promedio": round(float(result), 1) if result else 0}


def get_top_descripciones(db: Session, limite: int = 10, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    q = (
        db.query(
            OrdenServicio.descripcion,
            func.count(OrdenServicio.id).label("total"),
        )
        .filter(OrdenServicio.estado == "completada")
    )
    q = _apply_date_filter(q, OrdenServicio, fecha_inicio, fecha_fin)
    rows = q.group_by(OrdenServicio.descripcion).order_by(func.count(OrdenServicio.id).desc()).limit(limite).all()
    return [_to_dict(r, ["descripcion", "total"]) for r in rows]


def get_ordenes_por_dia_semana(db: Session):
    rows = (
        db.query(
            func.extract("dow", OrdenServicio.fecha_creacion).label("dia"),
            func.count(OrdenServicio.id).label("total"),
        )
        .group_by("dia")
        .order_by("dia")
        .all()
    )
    dias = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    counts = {i: 0 for i in range(7)}
    for r in rows:
        counts[int(r.dia)] = r.total
    return [{"dia": dias[i], "total": counts[i]} for i in range(7)]


def get_rendimiento_mecanicos(db: Session, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    q = (
        db.query(
            Mecanico.id,
            Mecanico.nombre,
            func.count(OrdenServicio.id).label("total_ordenes"),
            func.avg(
                func.extract("epoch", OrdenServicio.fecha_cierre - OrdenServicio.fecha_creacion)
                / 60
            ).label("minutos_promedio"),
        )
        .join(OrdenServicio, OrdenServicio.mecanico_id == Mecanico.id)
        .filter(
            OrdenServicio.estado == "completada",
            OrdenServicio.fecha_cierre.isnot(None),
        )
    )
    q = _apply_date_filter(q, OrdenServicio, fecha_inicio, fecha_fin)
    rows = q.group_by(Mecanico.id).order_by(func.count(OrdenServicio.id).desc()).all()
    return [_to_dict(r, ["id", "nombre", "total_ordenes", "minutos_promedio"]) for r in rows]
