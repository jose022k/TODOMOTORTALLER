from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.dao import ClienteDAO, MecanicoDAO
from app.modules.auth.schemas import UserUpdate
from app.modules.auth.utils import hash_password
from app.modules.users.schemas import ClienteDetailResponse, ClienteResponse, ClienteSummary, MotoAsociada
from app.modules.notifications.service import create_notification

cliente_dao = ClienteDAO()
mecanico_dao = MecanicoDAO()


def _build_motos(cliente):
    return [
        MotoAsociada(
            id=m.id,
            placa=m.placa,
            anio=m.anio,
            color=m.color,
            codigo_qr=m.codigo_qr,
            marca=m.catalogo_moto.marca,
            modelo=m.catalogo_moto.modelo,
            gama_color=m.catalogo_moto.gama_color,
        )
        for m in cliente.motos_cliente
    ]


def get_all_clients(db: Session, activo_only: bool = False, skip: int = 0, limit: int = 100):
    clientes = cliente_dao.get_all_with_motos(db, skip=skip, limit=limit)
    if activo_only:
        clientes = [c for c in clientes if c.activo]
    return [
        ClienteResponse(
            id=c.id,
            nombre=c.nombre,
            cedula=c.cedula,
            email=c.email,
            telefono=c.telefono,
            direccion=c.direccion,
            activo=c.activo,
            motos=_build_motos(c),
        )
        for c in clientes
    ]


def get_clients_summary(db: Session, activo_only: bool = False):
    clientes = cliente_dao.get_all(db)
    if activo_only:
        clientes = [c for c in clientes if c.activo]
    return [
        ClienteSummary(id=c.id, nombre=c.nombre, cedula=c.cedula)
        for c in clientes
    ]


def get_client_by_id(db: Session, client_id: int):
    cliente = cliente_dao.get_with_motos(db, client_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    motos = _build_motos(cliente)
    return ClienteDetailResponse(
        id=cliente.id,
        nombre=cliente.nombre,
        cedula=cliente.cedula,
        email=cliente.email,
        telefono=cliente.telefono,
        direccion=cliente.direccion,
        activo=cliente.activo,
        motos=motos,
    )


def update_client(db: Session, client_id: int, data: dict):
    cliente = cliente_dao.get_by_id(db, client_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    updated = cliente_dao.update(db, cliente, data)
    setattr(updated, "rol", "cliente")
    create_notification(db, "datos_actualizados", "Tus datos han sido actualizados por el administrador", cliente_id=client_id)
    return updated


def deactivate_client(db: Session, client_id: int):
    cliente = cliente_dao.get_by_id(db, client_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )
    nuevo_estado = not cliente.activo
    return cliente_dao.update(db, cliente, {"activo": nuevo_estado})


def get_all_mechanics(db: Session, activo_only: bool = False, skip: int = 0, limit: int = 100):
    query = mecanico_dao.get_all(db, skip=skip, limit=limit)
    if activo_only:
        query = [m for m in query if m.activo]
    return query


def get_mechanic_by_id(db: Session, mechanic_id: int):
    mecanico = mecanico_dao.get_by_id(db, mechanic_id)
    if not mecanico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mecánico no encontrado",
        )
    return mecanico


def update_mechanic(db: Session, mechanic_id: int, data: dict):
    mecanico = mecanico_dao.get_by_id(db, mechanic_id)
    if not mecanico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mecánico no encontrado",
        )
    updated = mecanico_dao.update(db, mecanico, data)
    setattr(updated, "rol", "mecanico")
    create_notification(db, "datos_actualizados", "Tus datos han sido actualizados por el administrador", mecanico_id=mechanic_id)
    return updated


def deactivate_mechanic(db: Session, mechanic_id: int):
    mecanico = mecanico_dao.get_by_id(db, mechanic_id)
    if not mecanico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mecánico no encontrado",
        )
    nuevo_estado = not mecanico.activo
    return mecanico_dao.update(db, mecanico, {"activo": nuevo_estado})


def get_my_motos(db: Session, current_user):
    if current_user.rol != "cliente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo clientes")
    cliente = cliente_dao.get_with_motos(db, current_user.id)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return _build_motos(cliente)


def register_mecanico(db: Session, nombre: str, email: str, password: str):
    existing = mecanico_dao.get_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user_data = {
        "nombre": nombre,
        "email": email,
        "contraseña": hash_password(password),
    }
    user = mecanico_dao.create(db, user_data)
    setattr(user, "rol", "mecanico")
    return user
