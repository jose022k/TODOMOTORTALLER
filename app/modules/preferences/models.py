from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from app.core.database import Base


class UserPreference(Base):
    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True, index=True)
    user_role = Column(String(20), nullable=False)
    user_id = Column(Integer, nullable=False)
    notify_messages = Column(Boolean, default=True, nullable=False)
    notify_orders = Column(Boolean, default=True, nullable=False)
    dark_mode = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_role", "user_id", name="uq_user_preference"),
    )
