from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/")
def get_reports_status():
    return {"module": "reports", "status": "active"}
