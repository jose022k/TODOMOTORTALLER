from pydantic import BaseModel


class PreferencesResponse(BaseModel):
    notify_messages: bool
    notify_orders: bool
    dark_mode: bool

    class Config:
        from_attributes = True


class PreferencesUpdate(BaseModel):
    notify_messages: bool | None = None
    notify_orders: bool | None = None
    dark_mode: bool | None = None
