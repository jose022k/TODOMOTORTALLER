from fastapi import APIRouter

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/")
def get_clients_status():
    return {"module": "clients", "status": "active"}
