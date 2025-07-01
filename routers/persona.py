import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, and_

from modules.persona.service import generate_character_person
from modules.transaction.dto import CREDIT_NEEDS, CreateTransactionRequest
from modules.transaction.service import (
    get_available_credits,
    update_credits_with_transaction,
)
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import get_db, AsyncSession
from shared.models.story import Story, Storyline
from shared.utils import clean_keys_from_dict

router = APIRouter(prefix="/persona", tags=["Persona"])
logger = logging.getLogger("persona.api")


@router.post(
    "",
    description="Create character persona. Expects story outline in the body as is.",
    deprecated=True,
)
async def request_persona_generation(req: Request):
    body = await req.json()

    if not body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "empty request body")

    persona = await generate_character_person(body)

    return persona


@router.get(
    "/{story_id}",
    description="Create character persona. Expects story outline in the body as is.",
)
async def request_persona_generation_for_story(
    story_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    available_credits = await get_available_credits(db, current_user.uid)
    if available_credits < CREDIT_NEEDS.PERSONA:
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

    storyline_dict = clean_keys_from_dict(storyline_dict)

    persona = await generate_character_person(storyline_dict)

    storyline_doc.character_personas = persona
    story_record.status = "draft:persona"

    await db.commit()
    await update_credits_with_transaction(
        db,
        CreateTransactionRequest(
            user_id=current_user.uid,
            amount=CREDIT_NEEDS.PERSONA,
            remarks="Character persona creation",
            transaction_ref=story_id,
        ),
    )

    return {
        "message": "Persona created",
        "story_id": story_id,
        "persona": persona,
    }
