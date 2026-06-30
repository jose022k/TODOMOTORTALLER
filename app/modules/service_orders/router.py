from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.modules.auth.dependencies import (
    get_current_user,
    get_current_admin,
    get_current_mecanico,
    AnyUser,
)
from app.modules.auth.models import Admin


class TrackerResponse(BaseModel):
    id: int
    estado: str
    descripcion: str
    fecha_creacion: datetime
    fecha_cierre: Optional[datetime] = None
    cliente_nombre: str
    mecanico_nombre: str
    moto_marca: str
    moto_modelo: str
    moto_placa: str
    moto_cliente_id: int
from app.modules.service_orders.schemas import (
    OrdenServicioCreate,
    OrdenServicioResponse,
    OrdenServicioListResponse,
    OrdenServicioDetailResponse,
    MechanicAssign,
    StatusUpdate,
)
from app.modules.service_orders import service

router = APIRouter(prefix="/service-orders", tags=["service_orders"])


@router.post("/", response_model=OrdenServicioResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrdenServicioCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Crea una nueva orden de servicio. Solo administradores."""
    return service.create_order(db, data, admin)


@router.get("/", response_model=List[OrdenServicioListResponse])
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: Optional[str] = None,
    cliente_id: Optional[int] = Query(None),
    mecanico_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    """Lista órdenes de servicio. Filtra según el rol del usuario."""
    return service.get_orders(db, current_user, skip=skip, limit=limit, estado=estado, cliente_id=cliente_id, mecanico_id=mecanico_id)


@router.get("/{order_id}", response_model=OrdenServicioDetailResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    """Obtiene una orden de servicio por ID con detalles completos."""
    return service.get_order_by_id(db, order_id, current_user)


@router.patch("/{order_id}/status", response_model=OrdenServicioResponse)
def update_status(
    order_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_mecanico),
):
    """Actualiza el estado de una orden de servicio.
    Accesible para administradores y mecánicos (solo sus órdenes)."""
    return service.update_order_status(db, order_id, data.estado, current_user)


@router.patch("/{order_id}/mechanic", response_model=OrdenServicioResponse)
def reassign_mechanic(
    order_id: int,
    data: MechanicAssign,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Reasigna un mecánico a una orden existente. Solo administradores."""
    return service.assign_mechanic(db, order_id, data.mecanico_id, admin)


@router.get("/{order_id}/tracker", response_model=TrackerResponse)
def tracker(
    order_id: int,
    db: Session = Depends(get_db),
):
    """Endpoint público para consultar estado de una orden desde el QR."""
    return service.get_order_tracker(db, order_id)


@router.get("/moto/{moto_cliente_id}/history", response_model=List[OrdenServicioListResponse])
def moto_history(
    moto_cliente_id: int,
    db: Session = Depends(get_db),
):
    """Endpoint público para obtener el historial de órdenes de una moto."""
    return service.get_moto_history(db, moto_cliente_id)
