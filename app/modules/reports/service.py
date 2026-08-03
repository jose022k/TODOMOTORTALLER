from datetime import datetime, timedelta
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


def get_ganancias_semana(db: Session):
    """Ganancias en USD de órdenes completadas, agrupadas por día, últimos 7 días."""
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    inicio = hoy - timedelta(days=6)

    rows = (
        db.query(
            func.date(OrdenServicio.fecha_creacion).label("dia"),
            func.sum(OrdenServicio.monto_usd).label("total_usd"),
        )
        .filter(
            OrdenServicio.estado == "completada",
            OrdenServicio.fecha_creacion >= inicio,
            OrdenServicio.fecha_creacion < hoy + timedelta(days=1),
        )
        .group_by("dia")
        .order_by("dia")
        .all()
    )

    por_dia = {str(r.dia): float(r.total_usd or 0) for r in rows}

    dias_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dias = []
    for i in range(7):
        fecha = inicio + timedelta(days=i)
        clave = fecha.strftime("%Y-%m-%d")
        dias.append({
            "dia": dias_nombres[fecha.weekday()],
            "fecha": clave,
            "total_usd": round(por_dia.get(clave, 0.0), 2),
        })
    return dias


def get_clientes_nuevos_vs_recurrentes(db: Session, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    """Proporción de clientes nuevos (primera visita) vs recurrentes (vuelven al taller)."""
    primeras = (
        db.query(
            OrdenServicio.cliente_id,
            func.min(OrdenServicio.fecha_creacion).label("primera_visita"),
        )
        .group_by(OrdenServicio.cliente_id)
        .all()
    )
    primeras_map = {cid: fecha for cid, fecha in primeras}

    q = db.query(OrdenServicio.cliente_id).distinct()
    if fecha_inicio:
        q = q.filter(OrdenServicio.fecha_creacion >= fecha_inicio)
    if fecha_fin:
        q = q.filter(OrdenServicio.fecha_creacion <= fecha_fin)
    visitaron = [r[0] for r in q.all()]

    nuevos = 0
    recurrentes = 0
    for cid in visitaron:
        primera = primeras_map.get(cid)
        if primera is None:
            continue
        if not fecha_inicio or primera >= fecha_inicio:
            nuevos += 1
        else:
            recurrentes += 1

    if not fecha_inicio:
        # Sin rango de fechas: se clasifica por total de órdenes históricas
        # (1 orden = nuevo, 2+ órdenes = recurrente)
        conteos = (
            db.query(
                OrdenServicio.cliente_id,
                func.count(OrdenServicio.id).label("total"),
            )
            .group_by(OrdenServicio.cliente_id)
            .all()
        )
        nuevos = sum(1 for _, t in conteos if t == 1)
        recurrentes = sum(1 for _, t in conteos if t > 1)

    total = nuevos + recurrentes

    def _pct(n):
        return round(n / total * 100, 1) if total else 0

    return [
        {"tipo": "Nuevos", "cantidad": nuevos, "porcentaje": _pct(nuevos)},
        {"tipo": "Recurrentes", "cantidad": recurrentes, "porcentaje": _pct(recurrentes)},
    ]
