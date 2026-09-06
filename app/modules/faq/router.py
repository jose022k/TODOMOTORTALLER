from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin
from app.modules.faq import service
from app.modules.faq.schemas import FaqCreate, FaqUpdate, FaqResponse

router = APIRouter(prefix="/faq", tags=["FAQ"])


@router.get("/", response_model=List[FaqResponse])
def list_faqs(db: Session = Depends(get_db)):
    """Obtiene la lista de preguntas frecuentes activas (Público)."""
    return service.get_all_faqs(db, include_inactive=False)


@router.get("/admin/all", response_model=List[FaqResponse])
def list_faqs_admin(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Obtiene todas las preguntas frecuentes incluyendo inactivas (Admin)."""
    return service.get_all_faqs(db, include_inactive=True)


@router.post("/", response_model=FaqResponse, status_code=status.HTTP_201_CREATED)
def create_faq(
    data: FaqCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Crea una nueva pregunta frecuente (Admin)."""
    return service.create_faq(db, data)


@router.put("/{faq_id}", response_model=FaqResponse)
def update_faq(
    faq_id: int,
    data: FaqUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Actualiza una pregunta frecuente existente (Admin)."""
    faq = service.update_faq(db, faq_id, data)
    if not faq:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return faq


@router.delete("/{faq_id}")
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Elimina una pregunta frecuente (Admin)."""
    ok = service.delete_faq(db, faq_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return {"message": "Pregunta eliminada exitosamente"}
