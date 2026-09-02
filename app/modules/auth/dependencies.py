from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.models import Admin, Cliente, Mecanico
from app.modules.auth.utils import decode_token
from app.modules.auth.service import get_user_by_id, validate_active_session
from typing import Union

security = HTTPBearer()

AnyUser = Union[Admin, Cliente, Mecanico]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AnyUser:
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    user_id = payload.get("sub")
    role = payload.get("role")
    jti = payload.get("jti")
    if not user_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = get_user_by_id(db, user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not validate_active_session(db, user.id, role):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión cerrada o iniciada en otro dispositivo",
        )
    return user


def get_current_admin(current_user: AnyUser = Depends(get_current_user)) -> Admin:
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def get_current_mecanico(current_user: AnyUser = Depends(get_current_user)) -> Union[Admin, Mecanico]:
    if current_user.rol not in ("admin", "mecanico"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mecanico or admin privileges required",
        )
    return current_user
