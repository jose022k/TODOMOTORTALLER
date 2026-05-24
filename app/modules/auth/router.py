from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/")
def get_auth_status():
    return {"module": "auth", "status": "active"}
