from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin
from app.modules.auth.models import Admin
from app.modules.users import service
from app.modules.users.schemas import (
    ClienteUpdate,
    MecanicoUpdate,
    MecanicoCreate,
    MecanicoResponse,
    ClienteResponse,
    ClienteDetailResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/mechanics", response_model=MecanicoResponse, status_code=201)
def register_mechanic(
    data: MecanicoCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.register_mecanico(db, data.nombre, data.email, data.password)


@router.get("/clients", response_model=List[ClienteResponse])
def list_clients(
    activo_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.get_all_clients(db, activo_only)


@router.get("/clients/{client_id}", response_model=ClienteDetailResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.get_client_by_id(db, client_id)


@router.patch("/clients/{client_id}", response_model=ClienteResponse)
def update_client(
    client_id: int,
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    update_data = data.model_dump(exclude_unset=True)
    return service.update_client(db, client_id, update_data)


@router.patch("/clients/{client_id}/deactivate", response_model=ClienteResponse)
def deactivate_client(
    client_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.deactivate_client(db, client_id)


@router.get("/mechanics", response_model=List[MecanicoResponse])
def list_mechanics(
    activo_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.get_all_mechanics(db, activo_only)


@router.get("/mechanics/{mechanic_id}", response_model=MecanicoResponse)
def get_mechanic(
    mechanic_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.get_mechanic_by_id(db, mechanic_id)


@router.patch("/mechanics/{mechanic_id}", response_model=MecanicoResponse)
def update_mechanic(
    mechanic_id: int,
    data: MecanicoUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    update_data = data.model_dump(exclude_unset=True)
    return service.update_mechanic(db, mechanic_id, update_data)


@router.patch("/mechanics/{mechanic_id}/deactivate", response_model=MecanicoResponse)
def deactivate_mechanic(
    mechanic_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.deactivate_mechanic(db, mechanic_id)
