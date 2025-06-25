from pydantic import BaseModel, Field


class RegisterUserPayload(BaseModel):
    email: str = Field(...)
    password: str = Field(...)


class LoginUserPayload(BaseModel):
    email: str = Field(...)
    password: str = Field(...)
