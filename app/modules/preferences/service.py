from sqlalchemy.orm import Session
from app.modules.preferences.models import UserPreference
from app.modules.preferences.schemas import PreferencesResponse, PreferencesUpdate


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
        return True

    if tipo in ("mensaje_recibido", "evidencia_enviada"):
        return pref.notify_messages
    if tipo in ("orden_creada", "orden_en_proceso", "orden_completada", "orden_cancelada", "datos_actualizados"):
        return pref.notify_orders

    return True
