import uuid
import random
import time
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.dao import AdminDAO, ClienteDAO, MecanicoDAO
from app.modules.auth.models import ActiveSession, PasswordResetCode
from app.modules.auth.schemas import UserCreate, UserLogin, UserUpdate, ClienteCreate
from app.modules.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.email_service import send_email, build_reset_password_html

# Rate limiting por IP para recuperación de contraseña (60 segundos entre solicitudes)
_ultimo_envio_por_ip: dict[str, float] = {}


def _puede_enviar_reset(ip: str) -> bool:
    """Verifica si han pasado 60 segundos desde el último envío desde esta IP."""
    ahora = time.time()
    ultimo = _ultimo_envio_por_ip.get(ip, 0)
    if ahora - ultimo < 60:
        return False
    _ultimo_envio_por_ip[ip] = ahora
    return True

admin_dao = AdminDAO()
cliente_dao = ClienteDAO()
mecanico_dao = MecanicoDAO()


def check_and_create_active_session(db: Session, user_id: int, role: str) -> str:
    # 1. Comprobar si ya existe una sesión activa en otro dispositivo
    existing = db.query(ActiveSession).filter(
        ActiveSession.user_id == user_id,
        ActiveSession.user_role == role,
    ).first()

    if existing:
        # Notificar al usuario con la sesión activa del intento de inicio de sesión
        try:
            from app.modules.notifications.service import create_notification
            kw = {f"{role}_id": user_id}
            create_notification(
                db,
                mensaje="⚠️ Alerta de Seguridad: Se ha detectado un intento de inicio de sesión no autorizado en otro dispositivo con tu cuenta.",
                tipo="seguridad",
                **kw
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una sesión activa con esta cuenta en otro dispositivo. Debe cerrar sesión en el otro dispositivo para poder ingresar.",
        )

    # 2. Registrar nueva sesión activa
    now = datetime.utcnow()
    jti = str(uuid.uuid4())
    expires_at = now + timedelta(days=365)
    new_session = ActiveSession(
        user_id=user_id,
        user_role=role,
        token_jti=jti,
        created_at=now,
        expires_at=expires_at,
    )
    db.add(new_session)
    db.commit()
    return jti


def remove_active_session(db: Session, user_id: int, role: str):
    db.query(ActiveSession).filter(
        ActiveSession.user_id == user_id,
        ActiveSession.user_role == role,
    ).delete()
    db.commit()


def validate_active_session(db: Session, user_id: int, role: str, jti: str = None) -> bool:
    active = db.query(ActiveSession).filter(
        ActiveSession.user_id == user_id,
        ActiveSession.user_role == role,
    ).first()
    return active is not None


def find_user_by_email(db: Session, email: str):
    admin = admin_dao.get_by_email(db, email)
    if admin: return admin, "admin", admin_dao
    mecanico = mecanico_dao.get_by_email(db, email)
    if mecanico: return mecanico, "mecanico", mecanico_dao
    cliente = cliente_dao.get_by_email(db, email)
    if cliente: return cliente, "cliente", cliente_dao
    return None, None, None


def find_user_by_nombre(db: Session, nombre: str):
    admin = admin_dao.get_by_nombre(db, nombre)
    if admin: return admin
    mecanico = mecanico_dao.get_by_nombre(db, nombre)
    if mecanico: return mecanico
    cliente = cliente_dao.get_by_nombre(db, nombre)
    if cliente: return cliente
    return None


ETIQUETAS_DISPONIBILIDAD = {
    "email": ("Este correo", "registrado"),
    "cedula": ("Esta cédula", "registrada"),
    "telefono": ("Este teléfono", "registrado"),
}


def check_disponibilidad(db: Session, campo: str, valor: str) -> dict:
    """Indica si un correo / cédula / teléfono está libre, para avisar al
    usuario mientras escribe (sin necesidad de pulsar el botón de registro)."""
    campo = (campo or "").strip().lower()
    valor = (valor or "").strip()

    if campo not in ETIQUETAS_DISPONIBILIDAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campo no válido. Use email, cedula o telefono.",
        )

    if not valor:
        return {"campo": campo, "valor": valor, "disponible": True, "detalle": ""}

    if campo == "email":
        encontrado, _, _ = find_user_by_email(db, valor.lower())
        ocupado = encontrado is not None
    else:
        columna = (
            cliente_dao.model.cedula if campo == "cedula" else cliente_dao.model.telefono
        )
        ocupado = db.query(cliente_dao.model).filter(columna == valor).first() is not None

    etiqueta, participio = ETIQUETAS_DISPONIBILIDAD[campo]
    return {
        "campo": campo,
        "valor": valor,
        "disponible": not ocupado,
        "detalle": "" if not ocupado else f"{etiqueta} ya está {participio}.",
    }


def get_user_by_id_and_role(db: Session, user_id, role: str):
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        return None, None

    if role == "admin":
        user = admin_dao.get_by_id(db, uid)
        dao = admin_dao
    elif role == "mecanico":
        user = mecanico_dao.get_by_id(db, uid)
        dao = mecanico_dao
    elif role == "cliente":
        user = cliente_dao.get_by_id(db, uid)
        dao = cliente_dao
    else:
        return None, None
    
    if user:
        setattr(user, "rol", role)
    return user, dao


def register_cliente(db: Session, data: ClienteCreate):
    existing, _, _ = find_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este correo ya está registrado.",
        )
    existing_nombre = find_user_by_nombre(db, data.nombre)
    if existing_nombre:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este nombre ya está en uso.",
        )
    existing_cedula = db.query(cliente_dao.model).filter(
        cliente_dao.model.cedula == data.cedula
    ).first()
    if existing_cedula:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta cédula ya está registrada.",
        )
    existing_telefono = db.query(cliente_dao.model).filter(
        cliente_dao.model.telefono == data.telefono
    ).first()
    if existing_telefono:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este teléfono ya está registrado.",
        )

    user_data = data.model_dump(exclude={"rol"})
    user_data["contraseña"] = hash_password(user_data.pop("password"))
    
    user = cliente_dao.create(db, user_data)
    setattr(user, "rol", "cliente")
    return user


def login(db: Session, data: UserLogin) -> dict:
    user, role, _ = find_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.contraseña):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if data.rol and role != data.rol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Credenciales no válidas para este tipo de usuario",
        )
    if hasattr(user, "activo") and not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado. Contacte al administrador.",
        )

    # Validar sesión única activa por dispositivo
    jti = check_and_create_active_session(db, user.id, role)

    access_token = create_access_token({"sub": str(user.id), "role": role, "jti": jti})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": role, "jti": jti})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def logout_session(db: Session, current_user):
    remove_active_session(db, current_user.id, current_user.rol)
    return {"message": "Sesión cerrada exitosamente"}


def refresh_token(db: Session, token: str) -> dict:
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user_id = payload.get("sub")
    role = payload.get("role")
    jti = payload.get("jti")
    
    user, _ = get_user_by_id_and_role(db, user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    # Cuenta desactivada: no se puede refrescar el token
    if hasattr(user, "activo") and not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado. Contacte al administrador.",
        )

    # Extender la expiración de la sesión activa en DB por 30 minutos más
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=30)
    db.query(ActiveSession).filter(
        ActiveSession.user_id == user.id,
        ActiveSession.user_role == role
    ).update({"expires_at": expires_at}, synchronize_session="fetch")
    db.commit()

    access_token = create_access_token({"sub": str(user.id), "role": role, "jti": jti})
    new_refresh_token = create_refresh_token({"sub": str(user.id), "role": role, "jti": jti})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def get_user_by_id(db: Session, user_id, role: str):
    user, _ = get_user_by_id_and_role(db, user_id, role)
    return user


def update_user(db: Session, user_id: str, role: str, data: UserUpdate):
    user, dao = get_user_by_id_and_role(db, user_id, role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        if not data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere la contraseña actual para cambiar la contraseña.",
            )
        if not verify_password(data.current_password, user.contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="La contraseña actual no es correcta.",
            )
        update_data["contraseña"] = hash_password(update_data.pop("password"))
        update_data.pop("current_password", None)
        # Invalidar todas las sesiones activas del usuario tras cambio de contraseña
        remove_active_session(db, user.id, role)

    updated_user = dao.update(db, user, update_data)
    setattr(updated_user, "rol", role)
    return updated_user


import urllib.request
import json


def verify_google_token(token: str, is_access_token: bool = False) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de Google no proporcionado.")
    
    if is_access_token:
        # Verificar access_token via API de UserInfo de Google
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    else:
        # Verificar ID token (credential) via tokeninfo
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                email = data.get("email")
                if not email:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token de Google no contiene un correo electrónico.")
                return {
                    "email": email.lower().strip(),
                    "name": data.get("name", "").strip(),
                    "sub": data.get("sub"),
                }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de Google no válido o expirado.",
        )


def authenticate_google_cliente(db: Session, data) -> dict:
    # Determinar qué tipo de token se recibió
    token = data.access_token or data.credential_token
    is_access_token = bool(data.access_token)
    google_info = verify_google_token(token, is_access_token=is_access_token)
    email = google_info["email"]

    admin = admin_dao.get_by_email(db, email)
    if admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este correo pertenece a una cuenta de Administrador. Debe iniciar sesión con contraseña.",
        )
    mecanico = mecanico_dao.get_by_email(db, email)
    if mecanico:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este correo pertenece a una cuenta de Mecánico. Debe iniciar sesión con contraseña.",
        )

    cliente = cliente_dao.get_by_email(db, email)
    if not cliente or not cliente.cedula or not cliente.telefono:
        return {
            "needs_profile_completion": True,
            "google_email": email,
            "google_name": (cliente.nombre if cliente else google_info["name"]),
        }

    if hasattr(cliente, "activo") and not cliente.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado. Contacte al administrador.",
        )

    jti = check_and_create_active_session(db, cliente.id, "cliente")
    access_token = create_access_token({"sub": str(cliente.id), "role": "cliente", "jti": jti})
    refresh_token = create_refresh_token({"sub": str(cliente.id), "role": "cliente", "jti": jti})
    return {
        "needs_profile_completion": False,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def complete_google_cliente_profile(db: Session, data) -> dict:
    token = data.access_token or data.credential_token
    is_access_token = bool(data.access_token)
    google_info = verify_google_token(token, is_access_token=is_access_token)
    email = google_info["email"]

    existing_cedula = db.query(cliente_dao.model).filter(
        cliente_dao.model.cedula == data.cedula,
        cliente_dao.model.email != email
    ).first()
    if existing_cedula:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta cédula ya está registrada.",
        )

    existing_telefono = db.query(cliente_dao.model).filter(
        cliente_dao.model.telefono == data.telefono,
        cliente_dao.model.email != email
    ).first()
    if existing_telefono:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este teléfono ya está registrado.",
        )

    cliente = cliente_dao.get_by_email(db, email)
    if cliente:
        cliente.cedula = data.cedula
        cliente.nombre = data.nombre
        cliente.telefono = data.telefono
        if data.direccion:
            cliente.direccion = data.direccion
        db.commit()
        db.refresh(cliente)
    else:
        new_client_dict = {
            "email": email,
            "nombre": data.nombre,
            "cedula": data.cedula,
            "contraseña": hash_password(str(uuid.uuid4())),
            "telefono": data.telefono,
            "direccion": data.direccion or "Sin dirección especificada",
            "activo": True,
        }
        cliente = cliente_dao.create(db, new_client_dict)

    if hasattr(cliente, "activo") and not cliente.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado. Contacte al administrador.",
        )

    jti = check_and_create_active_session(db, cliente.id, "cliente")
    access_token = create_access_token({"sub": str(cliente.id), "role": "cliente", "jti": jti})
    refresh_token = create_refresh_token({"sub": str(cliente.id), "role": "cliente", "jti": jti})
    return {
        "needs_profile_completion": False,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# ============================================================
# RECUPERACIÓN DE CONTRASEÑA
# ============================================================
def _resolve_user_by_email(db: Session, email: str):
    """Devuelve (user, role, dao) o (None, None, None) si no existe.
    Siempre responde igual para evitar enumerar correos."""
    admin = admin_dao.get_by_email(db, email)
    if admin:
        return admin, "admin", admin_dao
    mecanico = mecanico_dao.get_by_email(db, email)
    if mecanico:
        return mecanico, "mecanico", mecanico_dao
    cliente = cliente_dao.get_by_email(db, email)
    if cliente:
        return cliente, "cliente", cliente_dao
    return None, None, None


def forgot_password(db: Session, data, ip: str = "unknown") -> dict:
    """Solicita restablecimiento de contraseña. Responde siempre igual
    (éxito genérico) para no revelar qué correos están registrados."""
    # Rate limiting: 60 segundos entre solicitudes desde la misma IP
    if not _puede_enviar_reset(ip):
        return {
            "message": "Demasiadas solicitudes. Espera 60 segundos antes de intentar nuevamente.",
            "error": "rate_limit",
            "email_enviado": False,
        }

    user, role, _ = _resolve_user_by_email(db, data.email)

    # Si el usuario no existe o es admin, no enviamos nada (admin no se recupera por correo)
    if not user or role == "admin":
        return {"message": "Si el correo existe y no es de administrador, recibirás un código de recuperación."}

    # Generar código de 6 dígitos
    code = f"{random.randint(100000, 999999):06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Invalidar códigos previos para este email+rol
    db.query(PasswordResetCode).filter(
        PasswordResetCode.email == data.email,
        PasswordResetCode.role == role,
    ).delete()
    db.commit()

    # Guardar código hasheado
    reset_code = PasswordResetCode(
        email=data.email,
        code_hash=hash_password(code),
        role=role,
        attempts=0,
        expires_at=expires_at,
    )
    db.add(reset_code)
    db.commit()

    # Enviar correo
    html = build_reset_password_html(code, data.email)
    resultado = send_email(
        to_email=data.email,
        subject="Código de recuperación de contraseña — Todomotortaller",
        body_html=html,
    )

    if not resultado["ok"]:
        return {
            "message": "Error al enviar el código.",
            "error": resultado["error"],
            "email_enviado": False,
        }

    return {
        "message": "Si el correo existe y no es de administrador, recibirás un código de recuperación.",
        "email_enviado": True,
    }


def reset_password(db: Session, data) -> dict:
    """Valida el código y actualiza la contraseña. Cierra todas las sesiones activas."""
    user, role, _ = _resolve_user_by_email(db, data.email)
    if not user or role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido o expirado.",
        )

    # Buscar código válido (no expirado, intentos < 3)
    reset_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.email == data.email,
        PasswordResetCode.role == role,
        PasswordResetCode.expires_at > datetime.utcnow(),
        PasswordResetCode.attempts < 3,
    ).order_by(PasswordResetCode.created_at.desc()).first()

    if not reset_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido o expirado.",
        )

    # Verificar código
    if not verify_password(data.code, reset_code.code_hash):
        reset_code.attempts += 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código incorrecto.",
        )

    # Código válido: actualizar contraseña y eliminar el código usado
    user.contraseña = hash_password(data.new_password)
    db.delete(reset_code)
    db.commit()

    # Invalidar todas las sesiones activas del usuario
    remove_active_session(db, user.id, role)

    return {"message": "Contraseña actualizada exitosamente. Inicia sesión con tu nueva contraseña."}


def admin_reset_password(db: Session, data) -> dict:
    """El admin resetea la contraseña de un mecánico desde la vista de usuarios."""
    if data.role not in ("mecanico",):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede restablecer contraseña de mecánicos desde esta función.",
        )

    user, role, _ = get_user_by_id_and_role(db, data.user_id, data.role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    user.contraseña = hash_password(data.new_password)
    db.commit()

    # Invalidar todas las sesiones activas del usuario
    remove_active_session(db, user.id, data.role)

    return {"message": "Contraseña restablecida correctamente."}


def verify_email_for_reset(db: Session, email: str) -> dict:
    """Verifica si un email pertenece a un cliente o mecánico registrado
    (no admin) y si puede recuperar contraseña."""
    user, role, _ = _resolve_user_by_email(db, email)
    if not user:
        return {"existe": False, "rol": None, "puede_recuperar": False}
    if role == "admin":
        return {"existe": True, "rol": "admin", "puede_recuperar": False}
    # cliente o mecanico
    return {"existe": True, "rol": role, "puede_recuperar": True}

