from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, AnyUser
from app.modules.preferences.schemas import PreferencesResponse, PreferencesUpdate
from app.modules.preferences import service

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=PreferencesResponse)
def read_preferences(
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.get_preferences(db, current_user)


@router.put("/", response_model=PreferencesResponse)
def update_preferences(
    data: PreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.update_preferences(db, current_user, data)
