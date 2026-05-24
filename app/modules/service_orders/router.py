from fastapi import APIRouter

router = APIRouter(prefix="/service-orders", tags=["service_orders"])

@router.get("/")
def get_service_orders_status():
    return {"module": "service_orders", "status": "active"}
