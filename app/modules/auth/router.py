from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.schemas import (
    ClienteCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    RefreshRequest,
)
from app.modules.auth.service import (
    register_cliente,
    login,
    refresh_token,
    get_user_by_id,
    update_user,
)
from app.modules.auth.dependencies import get_current_user, get_current_admin, AnyUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register/cliente", response_model=UserResponse, status_code=201)
def register_new_cliente(
    data: ClienteCreate, 
    db: Session = Depends(get_db)
):
    return register_cliente(db, data)


@router.post("/login", response_model=TokenResponse)
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    return login(db, data)


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(data: RefreshRequest, db: Session = Depends(get_db)):
    return refresh_token(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: AnyUser = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: AnyUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_user(db, current_user.id, current_user.rol, data)
