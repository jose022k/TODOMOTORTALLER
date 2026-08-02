from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import base64
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_admin, AnyUser
from app.modules.auth.models import Admin
from app.modules.motorcycles.models import MotoCliente
from app.modules.users import service
from app.modules.users.schemas import (
    ClienteUpdate,
    MecanicoUpdate,
    MecanicoCreate,
    MecanicoResponse,
    ClienteResponse,
    ClienteDetailResponse,
    ClienteSummary,
    MotoAsociada,
    CountResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/mechanics", response_model=MecanicoResponse, status_code=201)
def register_mechanic(
    data: MecanicoCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.register_mecanico(db, data.nombre, data.email, data.password)


@router.get("/clients/count", response_model=CountResponse)
def count_clients(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    total = service.count_clients(db)
    return {"total": total}


@router.get("/clients", response_model=List[ClienteResponse])
def list_clients(
    activo_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.get_all_clients(db, activo_only, skip=skip, limit=limit)


@router.get("/clients/summary", response_model=List[ClienteSummary])
def list_clients_summary(
    activo_only: bool = False,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Versión ligera para dropdowns: solo id, nombre, cedula."""
    return service.get_clients_summary(db, activo_only)


@router.get("/clients/{client_id}", response_model=ClienteDetailResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.get_client_by_id(db, client_id)


@router.get("/clients/me/motos", response_model=List[MotoAsociada])
def my_motos(
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    """Devuelve las motos del cliente autenticado."""
    return service.get_my_motos(db, current_user)


@router.get("/clients/motos/{moto_cliente_id}/qr/download")
def download_moto_qr(
    moto_cliente_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    """Descarga el código QR de una moto como imagen PNG. Solo el cliente propietario."""
    if current_user.rol != "cliente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo clientes pueden descargar QR")
    moto = db.query(MotoCliente).filter(MotoCliente.id == moto_cliente_id).first()
    if not moto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moto no encontrada")
    if moto.cliente_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No eres el propietario de esta moto")
    if not moto.codigo_qr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Esta moto no tiene código QR")
    qr_base64 = moto.codigo_qr
    if qr_base64.startswith("data:image/png;base64,"):
        qr_base64 = qr_base64.split(",", 1)[1]
    qr_bytes = base64.b64decode(qr_base64)
    return Response(
        content=qr_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="QR_{moto.placa}.png"'},
    )


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


@router.get("/mechanics/count", response_model=CountResponse)
def count_mechanics(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    total = service.count_mechanics(db)
    return {"total": total}


@router.get("/mechanics", response_model=List[MecanicoResponse])
def list_mechanics(
    activo_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    return service.get_all_mechanics(db, activo_only, skip=skip, limit=limit)


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
