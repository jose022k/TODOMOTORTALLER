from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.dao import ClienteDAO, MecanicoDAO
from app.modules.auth.schemas import UserUpdate
from app.modules.auth.utils import hash_password

cliente_dao = ClienteDAO()
mecanico_dao = MecanicoDAO()


def get_all_clients(db: Session, activo_only: bool = False):
    query = cliente_dao.get_all(db)
    if activo_only:
        query = [c for c in query if c.activo]
    return query


def get_client_by_id(db: Session, client_id: int):
    cliente = cliente_dao.get_by_id(db, client_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    return cliente


def update_client(db: Session, client_id: int, data: dict):
    cliente = cliente_dao.get_by_id(db, client_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    updated = cliente_dao.update(db, cliente, data)
    setattr(updated, "rol", "cliente")
    return updated


def deactivate_client(db: Session, client_id: int):
    cliente = cliente_dao.get_by_id(db, client_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    nuevo_estado = not cliente.activo
    return cliente_dao.update(db, cliente, {"activo": nuevo_estado})


def get_all_mechanics(db: Session, activo_only: bool = False):
    query = mecanico_dao.get_all(db)
    if activo_only:
        query = [m for m in query if m.activo]
    return query


def get_mechanic_by_id(db: Session, mechanic_id: int):
    mecanico = mecanico_dao.get_by_id(db, mechanic_id)
    if not mecanico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mecánico no encontrado",
        )
    return mecanico


def update_mechanic(db: Session, mechanic_id: int, data: dict):
    mecanico = mecanico_dao.get_by_id(db, mechanic_id)
    if not mecanico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mecánico no encontrado",
        )
    updated = mecanico_dao.update(db, mecanico, data)
    setattr(updated, "rol", "mecanico")
    return updated


def deactivate_mechanic(db: Session, mechanic_id: int):
    mecanico = mecanico_dao.get_by_id(db, mechanic_id)
    if not mecanico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mecánico no encontrado",
        )
    nuevo_estado = not mecanico.activo
    return mecanico_dao.update(db, mecanico, {"activo": nuevo_estado})


def register_mecanico(db: Session, nombre: str, email: str, password: str):
    existing = mecanico_dao.get_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user_data = {
        "nombre": nombre,
        "email": email,
        "contraseña": hash_password(password),
    }
    user = mecanico_dao.create(db, user_data)
    setattr(user, "rol", "mecanico")
    return user
