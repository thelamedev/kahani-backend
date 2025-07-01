from sqlalchemy import UUID, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database import Base


class User(Base):
    __tablename__ = "users"

    first_name = Column(String)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    source = Column(String)
    source_id = Column(String, index=True)
    role: Mapped[str] = mapped_column(String, default="user")

    subscription = relationship("Subscription", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    display_name = Column(String)
    expires_at = Column(DateTime)
    credits: Mapped[float] = mapped_column(Float, default=20.0)

    user = relationship("User", back_populates="subscription")
