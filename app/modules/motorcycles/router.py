from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, get_current_admin, AnyUser
from app.modules.motorcycles.schemas import (
    BrandResponse,
    CatalogoMotoCreate,
    CatalogoMotoUpdate,
    CatalogoMotoResponse,
    MarcaResponse,
)
from app.modules.motorcycles.service import (
    get_brands,
    get_catalog_items,
    count_catalog_items,
    get_catalog_item_by_id,
    create_catalog_item,
    update_catalog_item,
    delete_catalog_item,
    create_brand,
)

router = APIRouter(prefix="/motorcycles", tags=["motorcycles"])


@router.get("/brands", response_model=List[BrandResponse])
def list_brands(
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return get_brands(db)


@router.post("/brands", response_model=MarcaResponse, status_code=status.HTTP_201_CREATED)
def create_brand_endpoint(
    nombre: str = Form(...),
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: AnyUser = Depends(get_current_admin),
):
    return create_brand(db, nombre, logo.file)


@router.get("/catalog/count")
def count_catalog(
    search: str = "",
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    total = count_catalog_items(db, search=search)
    return {"total": total}


@router.get("/catalog", response_model=List[CatalogoMotoResponse])
def list_catalog(
    skip: int = 0,
    limit: int = 100,
    search: str = "",
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return get_catalog_items(db, skip=skip, limit=limit, search=search)


@router.get("/catalog/{item_id}", response_model=CatalogoMotoResponse)
def get_catalog_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return get_catalog_item_by_id(db, item_id)


@router.post("/catalog", response_model=CatalogoMotoResponse, status_code=status.HTTP_201_CREATED)
def create_catalog(
    data: CatalogoMotoCreate,
    db: Session = Depends(get_db),
    admin: AnyUser = Depends(get_current_admin),
):
    return create_catalog_item(db, data)


@router.put("/catalog/{item_id}", response_model=CatalogoMotoResponse)
def update_catalog(
    item_id: int,
    data: CatalogoMotoUpdate,
    db: Session = Depends(get_db),
    admin: AnyUser = Depends(get_current_admin),
):
    return update_catalog_item(db, item_id, data)


@router.delete("/catalog/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_catalog(
    item_id: int,
    db: Session = Depends(get_db),
    admin: AnyUser = Depends(get_current_admin),
):
    delete_catalog_item(db, item_id)
    return
