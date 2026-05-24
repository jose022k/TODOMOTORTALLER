from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/")
def get_notifications_status():
    return {"module": "notifications", "status": "active"}
