import logging
from operator import and_
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select

from modules.script.service import generate_script
from modules.transaction.dto import CREDIT_NEEDS, CreateTransactionRequest
from modules.transaction.service import (
    get_available_credits,
    update_credits_with_transaction,
)
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import get_db, AsyncSession
from shared.models.story import Script, Story, Storyline
from shared.utils import clean_keys_from_dict

router = APIRouter(prefix="/script", tags=["Script"])
logger = logging.getLogger("script.api")


@router.post(
    "",
    description="Create Script with given 'story_outline', 'persona' and 'language'.",
    deprecated=True,
)
async def request_script_generation(req: Request):
    body = await req.json()

    if not body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "empty request body")

    story_outline = body.get("story_outline")
    persona = body.get("persona")
    language = body.get("language")

    if not story_outline:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'story_outline' is required")

    if not persona:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'persona' is required")

    if not language:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'language' is required")

    script = await generate_script(story_outline, persona, language)

    return {"script": script}


@router.get(
    "/{story_id}",
    description="Create Script with given 'story_outline', 'persona' and 'language'.",
)
async def request_script_generation_for_story(
    story_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    available_credits = await get_available_credits(db, current_user.uid)
    if available_credits < CREDIT_NEEDS.NARRATIVE:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "insufficient credits")

    story_uuid = uuid.UUID(hex=story_id)
    storyline_query = (
        select(Storyline)
        .where(
            and_(
                Storyline.story_id == story_uuid,
                Storyline.creator_id == current_user.uid,
            )
        )
        .limit(1)
    )
    storyline_result = await db.execute(storyline_query)

    storyline_row = storyline_result.first()
    if not storyline_row:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no storyline found for story")

    story_query = select(Story).where(Story.id == story_uuid).limit(1)
    story_record = (await db.execute(story_query)).scalar_one_or_none()
    if not story_record:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no story found for id")

    storyline_doc = storyline_row.tuple()[0]

    storyline_dict = {
        "plot_outline": storyline_doc.plot_outline,
        "characters": storyline_doc.characters,
        "theme": storyline_doc.theme,
        "mood": storyline_doc.mood,
        "setting": storyline_doc.setting,
        "moral": storyline_doc.tone,
        "conflict": storyline_doc.conflict,
        "resolution": storyline_doc.resolution,
        "style": storyline_doc.style,
    }

    story_outline = clean_keys_from_dict(storyline_dict)
    if len(story_outline) == 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "invalid or empty story outline"
        )

    persona = storyline_doc.character_personas
    if not persona:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid or empty persona")

    language = story_record.language
    if not language:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid or empty language")

    script = await generate_script(story_outline, persona, language)

    script_doc = Script(
        creator_id=current_user.uid,
        story_id=story_record.id,
        dialogues=script,
    )
    db.add(script_doc)

    story_record.status = "draft:script"

    await db.commit()
    await update_credits_with_transaction(
        db,
        CreateTransactionRequest(
            user_id=current_user.uid,
            amount=CREDIT_NEEDS.NARRATIVE,
            remarks="Story Narrative creation",
            transaction_ref=story_id,
        ),
    )

    return {
        "script": script,
        "story_id": story_id,
    }
