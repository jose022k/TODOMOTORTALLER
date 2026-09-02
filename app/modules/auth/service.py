import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.dao import AdminDAO, ClienteDAO, MecanicoDAO
from app.modules.auth.models import ActiveSession
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


def check_and_create_active_session(db: Session, user_id: int, role: str) -> str:
    # 1. Comprobar si ya existe una sesión activa en otro dispositivo
    existing = db.query(ActiveSession).filter(
        ActiveSession.user_id == user_id,
        ActiveSession.user_role == role,
    ).first()

    if existing:
        # Notificar al usuario con la sesión activa del intento de inicio de sesión
        try:
            from app.modules.notifications.service import create_notification
            kw = {f"{role}_id": user_id}
            create_notification(
                db,
                mensaje="⚠️ Alerta de Seguridad: Se ha detectado un intento de inicio de sesión no autorizado en otro dispositivo con tu cuenta.",
                tipo="seguridad",
                **kw
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una sesión activa con esta cuenta en otro dispositivo. Debe cerrar sesión en el otro dispositivo para poder ingresar.",
        )

    # 2. Registrar nueva sesión activa
    now = datetime.utcnow()
    jti = str(uuid.uuid4())
    expires_at = now + timedelta(days=365)
    new_session = ActiveSession(
        user_id=user_id,
        user_role=role,
        token_jti=jti,
        created_at=now,
        expires_at=expires_at,
    )
    db.add(new_session)
    db.commit()
    return jti


def remove_active_session(db: Session, user_id: int, role: str):
    db.query(ActiveSession).filter(
        ActiveSession.user_id == user_id,
        ActiveSession.user_role == role,
    ).delete()
    db.commit()


def validate_active_session(db: Session, user_id: int, role: str, jti: str = None) -> bool:
    active = db.query(ActiveSession).filter(
        ActiveSession.user_id == user_id,
        ActiveSession.user_role == role,
    ).first()
    return active is not None


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


def get_user_by_id_and_role(db: Session, user_id, role: str):
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        return None, None

    if role == "admin":
        user = admin_dao.get_by_id(db, uid)
        dao = admin_dao
    elif role == "mecanico":
        user = mecanico_dao.get_by_id(db, uid)
        dao = mecanico_dao
    elif role == "cliente":
        user = cliente_dao.get_by_id(db, uid)
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

    # Validar sesión única activa por dispositivo
    jti = check_and_create_active_session(db, user.id, role)

    access_token = create_access_token({"sub": str(user.id), "role": role, "jti": jti})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": role, "jti": jti})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def logout_session(db: Session, current_user):
    remove_active_session(db, current_user.id, current_user.rol)
    return {"message": "Sesión cerrada exitosamente"}


def refresh_token(db: Session, token: str) -> dict:
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user_id = payload.get("sub")
    role = payload.get("role")
    jti = payload.get("jti")
    
    user, _ = get_user_by_id_and_role(db, user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Extender la expiración de la sesión activa en DB por 30 minutos más
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=30)
    db.query(ActiveSession).filter(
        ActiveSession.user_id == user.id,
        ActiveSession.user_role == role
    ).update({"expires_at": expires_at}, synchronize_session="fetch")
    db.commit()

    access_token = create_access_token({"sub": str(user.id), "role": role, "jti": jti})
    new_refresh_token = create_refresh_token({"sub": str(user.id), "role": role, "jti": jti})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def get_user_by_id(db: Session, user_id, role: str):
    user, _ = get_user_by_id_and_role(db, user_id, role)
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
