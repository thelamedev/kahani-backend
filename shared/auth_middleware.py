import uuid
from fastapi import HTTPException, Header, status
from pydantic import BaseModel

from shared.jwt_utils import verify_token


class AuthUser(BaseModel):
    uid: uuid.UUID
    email: str

    @property
    def is_authenticated(self):
        return self.uid != ""


async def get_current_user(authorization: str | None = Header(None)) -> AuthUser:
    try:
        if not authorization:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing authorization")

        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "unsupported authentication scheme",
            )

        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "invalid or expired token",
            )

        if not isinstance(payload, dict):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "malformed payload",
            )

        uid = uuid.UUID(hex=payload["sub"])
        return AuthUser(uid=uid, email=payload.get("email", ""))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
