from fastapi import APIRouter

router = APIRouter(prefix="/mechanics", tags=["mechanics"])

@router.get("/")
def get_mechanics_status():
    return {"module": "mechanics", "status": "active"}
