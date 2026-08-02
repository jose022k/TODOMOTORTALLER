from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin
from app.modules.bcv import service

router = APIRouter(prefix="/bcv", tags=["BCV"])


class TasaManualIn(BaseModel):
    tasa: float


@router.get("/tasa")
def tasa_bcv(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Devuelve la tasa BCV actual (automática o manual)."""
    try:
        tasa, fuente = service.get_tasa(db)
        return {"tasa": tasa, "fuente": fuente}
    except ValueError as e:
        return {"tasa": None, "fuente": "no_disponible", "detalle": str(e)}


@router.put("/tasa-manual")
def set_tasa_manual(
    data: TasaManualIn,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Guarda la tasa manual de respaldo (override)."""
    if data.tasa <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tasa debe ser mayor que 0.",
        )
    service.set_tasa_manual(db, data.tasa)
    return {"tasa": data.tasa, "fuente": "manual"}
