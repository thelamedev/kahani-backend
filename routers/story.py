import math
import uuid
from operator import and_
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func

from routers.dtos.story import UpdateStoryPayload
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import get_db, AsyncSession
from shared.models.story import Story
from shared.pagination import Pagination, get_pagination

router = APIRouter(prefix="/story")


@router.get("/list")
async def list_stories_for_user(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(get_pagination),
):
    page_count_query = select(func.count(Story.id)).where(
        Story.creator_id == current_user.uid
    )
    page_count = (await db.execute(page_count_query)).scalar_one_or_none()
    if page_count is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "failed to get total count for the query",
        )

    query = (
        select(Story)
        .where(Story.creator_id == current_user.uid)
        .order_by(Story.created_at)
        .offset((pagination.page - 1) * pagination.limit)
        .limit(pagination.limit)
    )
    result = await db.execute(query)
    story_seq = result.all()

    story_list = [story.tuple()[0] for story in story_seq]

    return {
        "stories": story_list,
        "total_pages": math.ceil(page_count / pagination.limit),
    }


@router.patch("/{story_id}")
async def update_story_information(
    story_id: str,
    payload: UpdateStoryPayload,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    story_uuid = uuid.UUID(hex=story_id)
    query = (
        select(Story)
        .where(
            and_(
                Story.id == story_uuid,
                Story.creator_id == current_user.uid,
            )
        )
        .limit(1)
    )

    result = await db.execute(query)
    story_doc = result.scalar_one_or_none()

    if story_doc is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid story id")

    if payload.title:
        story_doc.title = payload.title

    if payload.description:
        story_doc.description = payload.description

    if payload.image_src:
        story_doc.image_src = payload.image_src

    await db.commit()

    return {"message": "Story record updated"}
