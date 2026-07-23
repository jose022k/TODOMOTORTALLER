from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin
from app.modules.reports import service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/mecanicos/mas-servicios")
def mecanicos_mas_servicios(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_mecanico_mas_servicios(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/motos/mas-atendidas")
def motos_mas_atendidas(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_motos_mas_atendidas(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/clientes/recurrentes")
def clientes_recurrentes(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_clientes_recurrentes(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/tiempo-promedio-reparacion")
def tiempo_promedio_reparacion(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_tiempo_promedio_reparacion(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/servicios/top-descripciones")
def top_descripciones(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    limite: int = 10,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_top_descripciones(db, limite, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get("/ordenes/por-dia-semana")
def ordenes_por_dia_semana(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_ordenes_por_dia_semana(db)


@router.get("/mecanicos/rendimiento")
def rendimiento_mecanicos(
    fecha_inicio: Optional[datetime] = Query(None),
    fecha_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_rendimiento_mecanicos(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
