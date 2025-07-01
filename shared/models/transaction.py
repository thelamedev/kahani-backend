from sqlalchemy import Column, UUID, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from shared.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    remarks = Column(String, nullable=False)
    transaction_ref: Mapped[String] = mapped_column(String, nullable=True)
