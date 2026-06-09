from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.dao import AdminDAO, ClienteDAO, MecanicoDAO
from app.modules.auth.schemas import UserCreate, UserLogin, UserUpdate, ClienteCreate
from app.modules.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

admin_dao = AdminDAO()
cliente_dao = ClienteDAO()
mecanico_dao = MecanicoDAO()


def find_user_by_email(db: Session, email: str):
    admin = admin_dao.get_by_email(db, email)
    if admin: return admin, "admin", admin_dao
    mecanico = mecanico_dao.get_by_email(db, email)
    if mecanico: return mecanico, "mecanico", mecanico_dao
    cliente = cliente_dao.get_by_email(db, email)
    if cliente: return cliente, "cliente", cliente_dao
    return None, None, None


def find_user_by_nombre(db: Session, nombre: str):
    admin = admin_dao.get_by_nombre(db, nombre)
    if admin: return admin
    mecanico = mecanico_dao.get_by_nombre(db, nombre)
    if mecanico: return mecanico
    cliente = cliente_dao.get_by_nombre(db, nombre)
    if cliente: return cliente
    return None


def get_user_by_id_and_role(db: Session, user_id: str, role: str):
    if role == "admin":
        user = admin_dao.get_by_id(db, user_id)
        dao = admin_dao
    elif role == "mecanico":
        user = mecanico_dao.get_by_id(db, user_id)
        dao = mecanico_dao
    elif role == "cliente":
        user = cliente_dao.get_by_id(db, user_id)
        dao = cliente_dao
    else:
        return None, None
    
    if user:
        setattr(user, "rol", role)
    return user, dao



def register_cliente(db: Session, data: ClienteCreate):
    existing, _, _ = find_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    existing_nombre = find_user_by_nombre(db, data.nombre)
    if existing_nombre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre already taken",
        )
    
    user_data = data.model_dump(exclude={"rol"})
    user_data["contraseña"] = hash_password(user_data.pop("password"))
    
    user = cliente_dao.create(db, user_data)
    setattr(user, "rol", "cliente")
    return user


def login(db: Session, data: UserLogin) -> dict:
    user, role, _ = find_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.contraseña):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if data.rol and role != data.rol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Credenciales no válidas para este tipo de usuario",
        )
    if hasattr(user, "activo") and not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado. Contacte al administrador.",
        )
    access_token = create_access_token({"sub": str(user.id), "role": role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": role})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_token(db: Session, token: str) -> dict:
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user_id = payload.get("sub")
    role = payload.get("role")
    
    user, _ = get_user_by_id_and_role(db, user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    access_token = create_access_token({"sub": str(user.id), "role": role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": role})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def get_user_by_id(db: Session, user_id: str, role: str):
    user, _ = get_user_by_id_and_role(db, user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def update_user(db: Session, user_id: str, role: str, data: UserUpdate):
    user, dao = get_user_by_id_and_role(db, user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
        
    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["contraseña"] = hash_password(update_data.pop("password"))
        
    updated_user = dao.update(db, user, update_data)
    setattr(updated_user, "rol", role)
    return updated_user
