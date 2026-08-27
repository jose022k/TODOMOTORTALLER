from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin
from app.modules.auth.models import Admin
from app.modules.admin import service
from app.modules.admin.schemas import DashboardResponse, DailyStatsResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return service.get_dashboard(db)


@router.get("/daily-stats", response_model=DailyStatsResponse)
def get_daily_stats(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return service.get_daily_stats(db)
