from operator import and_
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.user import Subscription, User


async def get_user_profile(db: AsyncSession, current_user: UUID):
    query = select(User).where(
        and_(
            User.id == current_user,
            User.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    user_doc = result.scalar_one_or_none()

    if user_doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")

    sub_query = (
        select(Subscription).where(Subscription.user_id == current_user).limit(1)
    )
    result = await db.execute(sub_query)
    subscription_doc = result.scalar_one_or_none()
    if subscription_doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "subscription not found")

    return {
        "profile": {
            "id": user_doc.id,
            "first_name": user_doc.first_name,
            "last_name": user_doc.last_name,
            "created_at": user_doc.created_at,
            "email": user_doc.email,
        },
        "subscription": {
            "display_name": subscription_doc.display_name,
            "expires_on": subscription_doc.expires_at,
            "available_credits": subscription_doc.credits,
        },
    }
