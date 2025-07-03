from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from modules.transaction.service import list_paginated_transactions
from shared.models.user import Subscription
from shared.pagination import Pagination, get_pagination
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import AsyncSession, get_db

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/list")
async def list_transactions(
    pagination: Pagination = Depends(get_pagination),
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    txns = await list_paginated_transactions(db, pagination, current_user.uid)
    return {
        "transactions": txns,
    }


@router.get("/reset/{user_id}")
async def reset_user_suubscription(
    user_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "superadmin":
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    user_uid = UUID(hex=user_id)
    check_sub_query = (
        select(Subscription.id).where(Subscription.user_id == user_uid).limit(1)
    )
    check_sub_result = await db.execute(check_sub_query)
    if check_sub_result.scalar_one_or_none() is not None:
        return {"message": "User subscription already exists"}

    create_user_sub = Subscription(
        user_id=user_uid,
        display_name="Early Adopter",
        expires_at=datetime.now() + timedelta(days=120),
    )
    db.add(create_user_sub)
    await db.commit()

    return create_user_sub
