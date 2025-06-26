import bcrypt

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from shared import jwt_utils
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import AsyncSession, get_db
from shared.models.user import Subscription, User
from routers.dtos.auth import LoginUserPayload, RegisterUserPayload


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, deprecated=True)
async def register_new_user(
    payload: RegisterUserPayload,
    db: AsyncSession = Depends(get_db),
):
    query = select(User.id).where(User.email == payload.email).limit(1)
    result = await db.execute(query)

    exists = result.scalars().first()
    if exists is not None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "email already exists")

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(payload.password.encode(), salt).decode()
    first_name = payload.email.split("@")[0]
    new_user_doc = User(
        first_name=first_name,
        last_name="",
        email=payload.email,
        password_hash=password_hash,
    )
    db.add(new_user_doc)
    await db.commit()

    query = select(User.id).where(User.email == payload.email)
    result = await db.execute(query)

    user_uid = result.scalar()
    if user_uid is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "failed to retrieve created user information",
        )

    subscription_doc = Subscription(
        user_id=user_uid,
        display_name="Early Adopter",
        expires_at=(datetime.now() + timedelta(days=30)),
    )
    db.add(subscription_doc)
    await db.commit()

    token = jwt_utils.generate_token(
        {
            "sub": str(user_uid),
            "email": payload.email,
        }
    )

    return {
        "token": token,
        "user": {
            "uid": user_uid,
            "email": payload.email,
        },
    }


@router.post("/login", status_code=status.HTTP_200_OK, deprecated=True)
async def login_user(payload: LoginUserPayload, db: AsyncSession = Depends(get_db)):
    query = (
        select(User.id, User.email, User.password_hash)
        .where(User.email == payload.email)
        .limit(1)
    )
    result = await db.execute(query)

    row = result.first()
    if not row:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid credentials")

    user_uid, user_email, password_hash = row.tuple()
    if not bcrypt.checkpw(payload.password.encode(), password_hash.encode()):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid credentials")

    token = jwt_utils.generate_token(
        {
            "sub": str(user_uid),
            "email": str(user_email),
        }
    )

    return {
        "token": token,
        "user": {
            "uid": user_uid,
            "email": str(user_email),
        },
    }


@router.get("/verify")
async def verify_auth(
    current_user: AuthUser = Depends(get_current_user),
):
    return {
        "message": "Verified",
        "current_user": current_user.model_dump(),
    }
