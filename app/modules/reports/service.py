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
    rows = q.group_by(Mecanico.id).order_by(func.avg(
        func.extract("epoch", OrdenServicio.fecha_cierre - OrdenServicio.fecha_creacion)
        / 60
    ).desc()).all()
    result = [_to_dict(r, ["id", "nombre", "minutos_promedio"]) for r in rows]
    for item in result:
        item["minutos_promedio"] = round(float(item["minutos_promedio"] or 0), 1)
    return result


def get_ganancias(db: Session, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    """
    Ganancias en USD de órdenes completadas, con agrupación dinámica según el rango:
      - <= 62 días: por día
      - 63 a 440 días: por semana
      - más de 440 días: por mes
    Si no hay filtros, se toma desde la primera orden hasta hoy.
    """
    q = (
        db.query(
            OrdenServicio.fecha_creacion,
            OrdenServicio.monto_usd,
        ).filter(OrdenServicio.estado == "completada")
    )
    if fecha_inicio:
        q = q.filter(OrdenServicio.fecha_creacion >= fecha_inicio)
    if fecha_fin:
        q = q.filter(OrdenServicio.fecha_creacion <= fecha_fin)

    rows = q.all()

    if not rows:
        # Rango por defecto (semana actual) para no devolver vacío
        hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start = hoy - timedelta(days=hoy.weekday())
        end = start + timedelta(days=5)
    else:
        fechas = [r[0] or datetime.utcnow() for r in rows]
        start = min(fechas).replace(hour=0, minute=0, second=0, microsecond=0)
        end = max(fechas).replace(hour=0, minute=0, second=0, microsecond=0)

    dias_totales = (end - start).days + 1
    key_format = "%Y-%m-%d"
    if dias_totales > 440:
        granularidad = "mes"
    elif dias_totales > 31:
        granularidad = "semana"
    else:
        granularidad = "dia"

    def _bucket(date_obj):
        d = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        if granularidad == "mes":
            return d.replace(day=1)
        if granularidad == "semana":
            return d - timedelta(days=d.weekday())
        return d

    acumulado = {}
    for r in rows:
        b = _bucket(r[0])
        acumulado[b] = acumulado.get(b, 0.0) + float(r[1] or 0)

    # Generar todos los buckets del rango (incluyendo los de 0)
    resultado = []
    inicio_bucket = _bucket(start)
    fin_bucket = _bucket(end)

    if granularidad == "dia":
        paso = timedelta(days=1)
        fmt = "%d/%m"
    elif granularidad == "semana":
        paso = timedelta(days=7)
        fmt = "%d/%m"
    else:
        paso = timedelta(days=1)

    punt = inicio_bucket
    while punt <= fin_bucket:
        total = round(acumulado.get(punt, 0.0), 2)
        if granularidad == "mes":
            label = punt.strftime("%b %Y")
        elif granularidad == "semana":
            label = punt.strftime("%d/%m")
        else:
            label = punt.strftime("%d/%m")
        resultado.append({
            "dia": label,
            "fecha": punt.strftime("%Y-%m-%d"),
            "total_usd": total,
        })
        if granularidad == "mes":
            if punt.month == 12:
                punt = punt.replace(year=punt.year + 1, month=1)
            else:
                punt = punt.replace(month=punt.month + 1)
        else:
            punt += paso

    return resultado


def get_ordenes_completadas_canceladas(db: Session, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None):
    """Cantidad y proporción de órdenes completadas vs canceladas."""
    q = db.query(
        OrdenServicio.estado,
        func.count(OrdenServicio.id).label("total"),
    ).filter(OrdenServicio.estado.in_(["completada", "cancelada"]))
    q = _apply_date_filter(q, OrdenServicio, fecha_inicio, fecha_fin)
    rows = q.group_by(OrdenServicio.estado).all()

    total_map = {"completada": 0, "cancelada": 0}
    for estado, total in rows:
        total_map[estado] = total

    completadas = total_map["completada"]
    canceladas = total_map["cancelada"]
    total = completadas + canceladas

    def _pct(n):
        return round(n / total * 100, 1) if total else 0

    return [
        {"tipo": "Completadas", "cantidad": completadas, "porcentaje": _pct(completadas)},
        {"tipo": "Canceladas", "cantidad": canceladas, "porcentaje": _pct(canceladas)},
    ]
