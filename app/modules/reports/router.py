from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin
from app.modules.reports import service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/mecanicos/mas-servicios")
def mecanicos_mas_servicios(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_mecanico_mas_servicios(db)


@router.get("/motos/mas-atendidas")
def motos_mas_atendidas(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_motos_mas_atendidas(db)


@router.get("/clientes/recurrentes")
def clientes_recurrentes(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_clientes_recurrentes(db)


@router.get("/tiempo-promedio-reparacion")
def tiempo_promedio_reparacion(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_tiempo_promedio_reparacion(db)


@router.get("/mecanicos/rendimiento")
def rendimiento_mecanicos(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return service.get_rendimiento_mecanicos(db)
