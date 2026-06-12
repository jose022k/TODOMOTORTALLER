from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.service_orders.models import OrdenServicio
from app.modules.motorcycles.models import MotoCliente, CatalogoMoto
from app.modules.auth.models import Cliente, Mecanico


def get_mecanico_mas_servicios(db: Session, limite: int = 5):
    return (
        db.query(
            Mecanico.id,
            Mecanico.nombre,
            func.count(OrdenServicio.id).label("total_servicios"),
        )
        .join(OrdenServicio, OrdenServicio.mecanico_id == Mecanico.id)
        .filter(OrdenServicio.estado == "completada")
        .group_by(Mecanico.id)
        .order_by(func.count(OrdenServicio.id).desc())
        .limit(limite)
        .all()
    )


def get_motos_mas_atendidas(db: Session, limite: int = 5):
    return (
        db.query(
            CatalogoMoto.marca,
            CatalogoMoto.modelo,
            func.count(OrdenServicio.id).label("total_ordenes"),
        )
        .select_from(CatalogoMoto)
        .join(MotoCliente, MotoCliente.catalogo_moto_id == CatalogoMoto.id)
        .join(OrdenServicio, OrdenServicio.moto_cliente_id == MotoCliente.id)
        .filter(OrdenServicio.estado == "completada")
        .group_by(CatalogoMoto.id)
        .order_by(func.count(OrdenServicio.id).desc())
        .limit(limite)
        .all()
    )


def get_clientes_recurrentes(db: Session, limite: int = 5):
    return (
        db.query(
            Cliente.id,
            Cliente.nombre,
            Cliente.cedula,
            func.count(OrdenServicio.id).label("total_ordenes"),
        )
        .join(OrdenServicio, OrdenServicio.cliente_id == Cliente.id)
        .group_by(Cliente.id)
        .order_by(func.count(OrdenServicio.id).desc())
        .limit(limite)
        .all()
    )


def get_tiempo_promedio_reparacion(db: Session):
    result = (
        db.query(
            func.avg(
                func.extract("epoch", OrdenServicio.fecha_cierre - OrdenServicio.fecha_creacion)
                / 3600
            ).label("horas_promedio")
        )
        .filter(
            OrdenServicio.estado == "completada",
            OrdenServicio.fecha_cierre.isnot(None),
        )
        .scalar()
    )
    return {"horas_promedio": round(result, 2) if result else 0}


def get_rendimiento_mecanicos(db: Session):
    return (
        db.query(
            Mecanico.id,
            Mecanico.nombre,
            func.count(OrdenServicio.id).label("total_ordenes"),
            func.avg(
                func.extract("epoch", OrdenServicio.fecha_cierre - OrdenServicio.fecha_creacion)
                / 3600
            ).label("horas_promedio"),
        )
        .join(OrdenServicio, OrdenServicio.mecanico_id == Mecanico.id)
        .filter(
            OrdenServicio.estado == "completada",
            OrdenServicio.fecha_cierre.isnot(None),
        )
        .group_by(Mecanico.id)
        .order_by(func.count(OrdenServicio.id).desc())
        .all()
    )
