from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.base_dao import BaseDAO
from app.modules.motorcycles.models import CatalogoMoto, Marca
from app.modules.motorcycles.schemas import CatalogoMotoCreate, CatalogoMotoUpdate


class CatalogoMotoDAO(BaseDAO[CatalogoMoto, CatalogoMotoCreate, CatalogoMotoUpdate]):
    def __init__(self):
        super().__init__(CatalogoMoto)

    def get_all_brands(self, db: Session) -> list:
        return (
            db.query(self.model.marca, self.model.logo_url)
            .distinct()
            .all()
        )

    def get_by_marca_modelo_color(
        self, db: Session, marca: str, modelo: str, gama_color: str
    ) -> Optional[CatalogoMoto]:
        return (
            db.query(self.model)
            .filter(
                self.model.marca == marca,
                self.model.modelo == modelo,
                self.model.gama_color == gama_color,
            )
            .first()
        )

    def get_all_paginated(self, db: Session, skip: int, limit: int, search: str = ""):
        query = db.query(self.model)
        if len(search) >= 2:
            pattern = f"{search}%"
            query = query.filter(
                or_(
                    self.model.marca.ilike(pattern),
                    self.model.modelo.ilike(pattern),
                )
            )
        return query.order_by(self.model.marca, self.model.modelo).offset(skip).limit(limit).all()

    def count_all(self, db: Session, search: str = ""):
        query = db.query(self.model.id)
        if len(search) >= 2:
            pattern = f"{search}%"
            query = query.filter(
                or_(
                    self.model.marca.ilike(pattern),
                    self.model.modelo.ilike(pattern),
                )
            )
        return query.count()


class MarcaDAO(BaseDAO[Marca, dict, dict]):
    def __init__(self):
        super().__init__(Marca)

    def get_by_nombre(self, db: Session, nombre: str):
        return db.query(self.model).filter(self.model.nombre == nombre).first()
