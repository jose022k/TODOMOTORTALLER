from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.modules.motorcycles.dao import CatalogoMotoDAO
from app.modules.motorcycles.schemas import CatalogoMotoCreate, CatalogoMotoUpdate

catalogo_dao = CatalogoMotoDAO()

def get_catalog_items(db: Session, skip: int = 0, limit: int = 100):
    return catalogo_dao.get_all(db, skip=skip, limit=limit)

def get_catalog_item_by_id(db: Session, item_id: int):
    item = catalogo_dao.get_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo de moto no encontrado en el catálogo"
        )
    return item

def create_catalog_item(db: Session, data: CatalogoMotoCreate):
    existing = catalogo_dao.get_by_marca_modelo_color(
        db, marca=data.marca, modelo=data.modelo, gama_color=data.gama_color
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un modelo de moto en el catálogo con la misma marca, modelo y gama de color"
        )
    return catalogo_dao.create(db, data)

def update_catalog_item(db: Session, item_id: int, data: CatalogoMotoUpdate):
    item = get_catalog_item_by_id(db, item_id)
    
    if data.marca or data.modelo or data.gama_color:
        marca = data.marca if data.marca is not None else item.marca
        modelo = data.modelo if data.modelo is not None else item.modelo
        gama_color = data.gama_color if data.gama_color is not None else item.gama_color
        
        existing = catalogo_dao.get_by_marca_modelo_color(
            db, marca=marca, modelo=modelo, gama_color=gama_color
        )
        if existing and existing.id != item_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro modelo de moto en el catálogo con la misma marca, modelo y gama de color"
            )
            
    return catalogo_dao.update(db, item, data)

def delete_catalog_item(db: Session, item_id: int):
    item = get_catalog_item_by_id(db, item_id)
    try:
        if item.motos_cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el modelo del catálogo porque tiene motocicletas de clientes asociadas."
            )
        return catalogo_dao.delete(db, item_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el modelo debido a restricciones de integridad referencial."
        )
