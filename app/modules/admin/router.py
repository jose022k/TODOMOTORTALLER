from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/")
def get_admin_status():
    return {"module": "admin", "status": "active"}
