from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, AnyUser
from app.modules.chat.schemas import MensajeCreate, MensajeEdit, MensajeResponse, EvidenciaResponse
from app.modules.chat import service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/{orden_id}", response_model=list[MensajeResponse])
def list_messages(
    orden_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.get_messages(db, orden_id, current_user)


@router.post("/{orden_id}", response_model=MensajeResponse, status_code=201)
def send_message(
    orden_id: int,
    data: MensajeCreate,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.send_message(db, orden_id, data.contenido, current_user)


@router.get("/{orden_id}/evidencias", response_model=list[EvidenciaResponse])
def list_evidencias(
    orden_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.get_evidencias(db, orden_id, current_user)


@router.post("/{orden_id}/evidencias", response_model=EvidenciaResponse, status_code=201)
def create_evidencia(
    orden_id: int,
    file: UploadFile = File(...),
    mensaje_id: int = Form(None),
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.create_evidencia(db, orden_id, file, mensaje_id, current_user)


@router.put("/{orden_id}/{mensaje_id}", response_model=MensajeResponse)
def edit_message(
    orden_id: int,
    mensaje_id: int,
    data: MensajeEdit,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.edit_message(db, orden_id, mensaje_id, data.contenido, current_user)


@router.patch("/{orden_id}/evidencias/{evidencia_id}/link", response_model=EvidenciaResponse)
def link_evidencia(
    orden_id: int,
    evidencia_id: int,
    mensaje_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    return service.link_evidencia(db, orden_id, evidencia_id, mensaje_id, current_user)


@router.delete("/{orden_id}/evidencias/{evidencia_id}", status_code=204)
def delete_evidencia(
    orden_id: int,
    evidencia_id: int,
    db: Session = Depends(get_db),
    current_user: AnyUser = Depends(get_current_user),
):
    service.delete_evidencia(db, orden_id, evidencia_id, current_user)
