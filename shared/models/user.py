from sqlalchemy import UUID, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from shared.database import Base


class User(Base):
    __tablename__ = "users"

    first_name = Column(String)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    subscription = relationship("Subscription", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    display_name = Column(String)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="subscription")
