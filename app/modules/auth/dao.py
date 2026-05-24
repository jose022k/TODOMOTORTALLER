from typing import Optional
from sqlalchemy.orm import Session
from app.core.base_dao import BaseDAO
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserUpdate


class UserDAO(BaseDAO[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(self.model).filter(self.model.username == username).first()
