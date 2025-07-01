from enum import Enum
from uuid import UUID
from pydantic import BaseModel


class CREDIT_NEEDS(Enum, int):
    OVERALL = 17
    STORYLINE = 3
    METADATA = 2
    PERSONA = 3
    NARRATIVE = 4
    VOICE = 5


class CreateTransactionRequest(BaseModel):
    user_id: UUID
    amount: float
    remarks: str
    transaction_ref: str = ""
