from base64 import b64decode
import uuid
from fastapi import Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy import select

from shared.database import get_db, AsyncSession
from shared.models import User


class AuthUser(BaseModel):
    uid: uuid.UUID
    email: str
    role: str = "user"

    @property
    def is_authenticated(self):
        return self.uid != ""


async def get_current_user(
    authorization: str = Header(),
    db: AsyncSession = Depends(get_db),
) -> AuthUser:
    try:
        if not authorization:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing authorization")

        scheme, credentials = authorization.split()

        match scheme.lower():
            case "bearer":
                return await bearer_scheme(db, credentials)
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


async def bearer_scheme(db: AsyncSession, token: str) -> AuthUser:
    user_id = b64decode(token).decode()

    return await verify_user_id(db, user_id)


async def basic_scheme(db: AsyncSession, token: str) -> AuthUser:
    decoded_token = b64decode(token)
    user_id, _ = decoded_token.split(b":")

    return await verify_user_id(db, user_id.decode())


async def verify_user_id(db: AsyncSession, user_id: str) -> AuthUser:
    user_query = (
        select(User.id, User.email, User.role).where(User.source_id == user_id).limit(1)
    )
    result = await db.execute(user_query)

    user_row = result.first()
    if user_row is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "invalid user credentails",
        )

    result.close()

    user_uuid, user_email, user_role = user_row.tuple()

    return AuthUser(uid=user_uuid, email=user_email, role=user_role)
