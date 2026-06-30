from typing import Optional
from sqlalchemy.orm import Session
from app.core.base_dao import BaseDAO
from app.modules.motorcycles.models import CatalogoMoto
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
