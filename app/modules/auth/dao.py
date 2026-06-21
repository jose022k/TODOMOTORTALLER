from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from app.core.base_dao import BaseDAO
from app.modules.auth.models import Admin, Cliente, Mecanico
from app.modules.motorcycles.models import MotoCliente
from app.modules.auth.schemas import AdminCreate, ClienteCreate, MecanicoCreate, UserUpdate

class AdminDAO(BaseDAO[Admin, AdminCreate, UserUpdate]):
    def __init__(self):
        super().__init__(Admin)

    def get_by_email(self, db: Session, email: str) -> Optional[Admin]:
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_nombre(self, db: Session, nombre: str) -> Optional[Admin]:
        return db.query(self.model).filter(self.model.nombre == nombre).first()


class ClienteDAO(BaseDAO[Cliente, ClienteCreate, UserUpdate]):
    def __init__(self):
        super().__init__(Cliente)

    def get_by_email(self, db: Session, email: str) -> Optional[Cliente]:
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_nombre(self, db: Session, nombre: str) -> Optional[Cliente]:
        return db.query(self.model).filter(self.model.nombre == nombre).first()

    def get_all_with_motos(self, db: Session) -> List[Cliente]:
        return (
            db.query(self.model)
            .options(selectinload(Cliente.motos_cliente).selectinload(MotoCliente.catalogo_moto))
            .all()
        )

    def get_with_motos(self, db: Session, client_id: int) -> Optional[Cliente]:
        return (
            db.query(self.model)
            .options(selectinload(Cliente.motos_cliente).selectinload(MotoCliente.catalogo_moto))
            .filter(self.model.id == client_id)
            .first()
        )


class MecanicoDAO(BaseDAO[Mecanico, MecanicoCreate, UserUpdate]):
    def __init__(self):
        super().__init__(Mecanico)

    def get_by_email(self, db: Session, email: str) -> Optional[Mecanico]:
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_nombre(self, db: Session, nombre: str) -> Optional[Mecanico]:
        return db.query(self.model).filter(self.model.nombre == nombre).first()
