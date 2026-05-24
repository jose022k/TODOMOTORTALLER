from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/")
def get_chat_status():
    return {"module": "chat", "status": "active"}
