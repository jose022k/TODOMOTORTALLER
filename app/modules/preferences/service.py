from sqlalchemy.orm import Session
from app.modules.preferences.models import UserPreference
from app.modules.preferences.schemas import PreferencesResponse, PreferencesUpdate

MESSAGE_TIPOS = ("mensaje_recibido", "evidencia_enviada")
ORDER_TIPOS = (
    "orden_creada",
    "orden_en_proceso",
    "orden_completada",
    "orden_cancelada",
    "orden_actualizada",
    "datos_actualizados",
    "mecanico_registrado",
    "catalogo_actualizado",
    "mecanico_reasignado",
)


def _defaults():
    return PreferencesResponse(notify_messages=True, notify_orders=True, dark_mode=False)


def get_preferences(db: Session, current_user) -> PreferencesResponse:
    pref = db.query(UserPreference).filter(
        UserPreference.user_role == current_user.rol,
        UserPreference.user_id == current_user.id,
    ).first()
    if not pref:
        return _defaults()
    return PreferencesResponse.model_validate(pref)


def update_preferences(db: Session, current_user, data: PreferencesUpdate) -> PreferencesResponse:
    pref = db.query(UserPreference).filter(
        UserPreference.user_role == current_user.rol,
        UserPreference.user_id == current_user.id,
    ).first()

    if not pref:
        pref = UserPreference(
            user_role=current_user.rol,
            user_id=current_user.id,
            notify_messages=True,
            notify_orders=True,
            dark_mode=False,
        )
        db.add(pref)

    if data.notify_messages is not None:
        pref.notify_messages = data.notify_messages
    if data.notify_orders is not None:
        pref.notify_orders = data.notify_orders
    if data.dark_mode is not None:
        pref.dark_mode = data.dark_mode

    db.commit()
    db.refresh(pref)
    return PreferencesResponse.model_validate(pref)


def should_notify(db: Session, user_role: str, user_id: int, tipo: str) -> bool:
    pref = db.query(UserPreference).filter(
        UserPreference.user_role == user_role,
        UserPreference.user_id == user_id,
    ).first()

    if not pref:
        return True  # Default: notify everything

    if tipo in MESSAGE_TIPOS:
        return True if pref.notify_messages is None else bool(pref.notify_messages)
    if tipo in ORDER_TIPOS:
        return True if pref.notify_orders is None else bool(pref.notify_orders)

    return True


def allowed_tipos(db: Session, user_role: str, user_id: int) -> set:
    """Devuelve el set de tipos de notificación permitidos según las preferencias del usuario."""
    pref = db.query(UserPreference).filter(
        UserPreference.user_role == user_role,
        UserPreference.user_id == user_id,
    ).first()

    if not pref:
        return None  # No preference row = allow all

    allowed = set()
    if pref.notify_messages is not False:
        allowed.update(MESSAGE_TIPOS)
    if pref.notify_orders is not False:
        allowed.update(ORDER_TIPOS)
    return allowed
