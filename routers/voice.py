import logging
from operator import and_
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select

from modules.transaction.dto import CREDIT_NEEDS, CreateTransactionRequest
from modules.transaction.service import (
    get_available_credits,
    update_credits_with_transaction,
)
from modules.voice.service import generate_voice_for_script
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import get_db, AsyncSession
from shared.language_codes import LANGUAGE_CODES
from shared.models.story import Script, Story, Storyline

router = APIRouter(prefix="/voice", tags=["Voice"])
logger = logging.getLogger("voice.api")


@router.post(
    "",
    description="Create Voice with given 'script', 'persona' and 'language'.",
    deprecated=True,
)
async def request_voice_generation(req: Request):
    body = await req.json()

    if not body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "empty request body")

    script = body.get("script")
    if not script:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'script' is required")
    if not isinstance(script, list):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "'script' should be a list of dialog objects."
        )

    persona = body.get("persona")
    if not persona:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'persona' is required")

    language = body.get("language")
    if not language:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'language' is required")
    if language not in LANGUAGE_CODES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "unknown value for 'language'")

    voice_path = await generate_voice_for_script(script, persona, language)

    return {"audio_path": voice_path}


@router.get(
    "/{story_id}",
    description="Create Voice with given 'script', 'persona' and 'language'.",
)
async def request_voice_generation_by_story(
    story_id: str,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    available_credits = await get_available_credits(db, current_user.uid)
    if available_credits < CREDIT_NEEDS.VOICE:
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

    storyline_doc = storyline_result.scalar_one_or_none()
    if not storyline_doc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no storyline found for story")

    story_query = select(Story).where(Story.id == story_uuid).limit(1)
    result = await db.execute(story_query)
    story_record = result.scalar_one_or_none()
    if not story_record:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no story record found")

    script_query = select(Script).where(Script.story_id == story_uuid).limit(1)
    result = await db.execute(script_query)
    script_record = result.scalar_one_or_none()
    if not script_record:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no script record found")

    script = script_record.dialogues
    if not script:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no script dialogues found")
    if not isinstance(script, list):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no script dialogues found")

    persona = storyline_doc.character_personas
    if not persona:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no character persona found")

    language = story_record.language
    if not language:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no language found")
    if language not in LANGUAGE_CODES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "unknown value for 'language'")

    voice_path = await generate_voice_for_script(script, persona, language)

    story_record.audio_src = voice_path
    story_record.status = "completed"
    await db.commit()

    await update_credits_with_transaction(
        db,
        CreateTransactionRequest(
            user_id=current_user.uid,
            amount=CREDIT_NEEDS.VOICE,
            remarks="Story Voice creation",
            transaction_ref=story_id,
        ),
    )

    return {"audio_path": voice_path}
