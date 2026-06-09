from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_admin, AnyUser
from app.modules.motorcycles.schemas import (
    CatalogoMotoCreate,
    CatalogoMotoUpdate,
    CatalogoMotoResponse,
)
from app.modules.motorcycles.service import (
    get_catalog_items,
    get_catalog_item_by_id,
    create_catalog_item,
    update_catalog_item,
    delete_catalog_item,
)

router = APIRouter(prefix="/motorcycles", tags=["motorcycles"])

@router.get("/catalog", response_model=List[CatalogoMotoResponse])
def list_catalog(
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    """Obtiene todos los modelos de moto registrados en el catálogo.
    Cualquier usuario autenticado puede consultarlo."""
    return get_catalog_items(db, skip=skip, limit=limit)

@router.get("/catalog/{item_id}", response_model=CatalogoMotoResponse)
def get_catalog_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    """Obtiene un modelo específico del catálogo por su ID.
    Cualquier usuario autenticado puede consultarlo."""
    return get_catalog_item_by_id(db, item_id)

@router.post("/catalog", response_model=CatalogoMotoResponse, status_code=status.HTTP_201_CREATED)
def create_catalog(
    data: CatalogoMotoCreate,
    db: Session = Depends(get_db),
    admin: AnyUser = Depends(get_current_admin),
):
    """Crea un nuevo modelo de moto en el catálogo.
    Solo accesible para administradores."""
    return create_catalog_item(db, data)

@router.put("/catalog/{item_id}", response_model=CatalogoMotoResponse)
def update_catalog(
    item_id: int,
    data: CatalogoMotoUpdate,
    db: Session = Depends(get_db),
    admin: AnyUser = Depends(get_current_admin),
):
    """Actualiza un modelo de moto en el catálogo.
    Solo accesible para administradores."""
    return update_catalog_item(db, item_id, data)

@router.delete("/catalog/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_catalog(
    item_id: int,
    db: Session = Depends(get_db),
    admin: AnyUser = Depends(get_current_admin),
):
    """Elimina un modelo de moto del catálogo.
    Solo accesible para administradores. No se puede eliminar si ya está asociado a motos de clientes."""
    delete_catalog_item(db, item_id)
    return
