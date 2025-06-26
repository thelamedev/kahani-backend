import uuid
from fastapi import Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy import select

from shared.jwt_utils import verify_token
from shared.database import get_db, AsyncSession
from shared.models import User


class AuthUser(BaseModel):
    uid: uuid.UUID
    email: str

    @property
    def is_authenticated(self):
        return self.uid != ""


async def get_current_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> AuthUser:
    try:
        if not authorization:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing authorization")

        scheme, credentials = authorization.split()

        match scheme.lower():
            case "bearer":
                return bearer_scheme(credentials)
            case "basic":
                return await basic_scheme(db, credentials)

        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "unsupported authentication scheme",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


def bearer_scheme(token: str) -> AuthUser:
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


async def basic_scheme(db: AsyncSession, token: str) -> AuthUser:
    user_query = select(User.id, User.email).where(User.source_id == token).limit(1)
    result = await db.execute(user_query)

    user_row = result.first()
    if user_row is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "invalid user credentails",
        )

    user_uuid, user_email = user_row.tuple()

    return AuthUser(uid=user_uuid, email=user_email)
