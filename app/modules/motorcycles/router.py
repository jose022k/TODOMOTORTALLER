from fastapi import APIRouter

router = APIRouter(prefix="/motorcycles", tags=["motorcycles"])

@router.get("/")
def get_motorcycles_status():
    return {"module": "motorcycles", "status": "active"}
