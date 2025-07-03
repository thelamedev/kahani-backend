from operator import and_
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.user import Subscription, User


async def get_user_profile(db: AsyncSession, current_user_uid: UUID):
    query = (
        select(User, Subscription)
        .where(
            and_(
                User.id == current_user_uid,
                User.deleted_at.is_(None),
            )
        )
        .join(Subscription, Subscription.user_id == User.id)
        .limit(1)
    )
    result = await db.execute(query)
    result_row = result.first()
    if result_row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")

    user_doc, subscription_doc = result_row.tuple()

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
