import asyncio
import logging
from typing import Annotated
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, status

from modules.transaction.dto import CREDIT_NEEDS, CreateTransactionRequest
from modules.transaction.service import (
    get_available_credits,
    update_credits_with_transaction,
)
from modules.metadata.service import (
    generate_image_for_story,
    generate_metadata_for_storyline,
)
from modules.storyline.service import generate_story_outline
from routers.dtos.storyline import StorylineRequestPayload
from shared.database import AsyncSession, get_db
from shared.models.story import Story, Storyline
from shared.auth_middleware import AuthUser, get_current_user

router = APIRouter(prefix="/storyline", tags=["Storyline"])
logger = logging.getLogger("storyline.api")


@router.post(
    "",
    description="Create Storyline with given 'user_input'.",
)
async def request_storyline_generation(
    payload: Annotated[StorylineRequestPayload, Body()],
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not payload.user_input:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    available_credits = await get_available_credits(db, current_user.uid)
    if available_credits < CREDIT_NEEDS.OVERALL:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "insufficient credits")

    storyline = await generate_story_outline(payload.user_input)

    story = Story(
        id=uuid.uuid4(),
        creator_id=current_user.uid,
        user_input=payload.user_input,
        language=payload.language,
        title="",
        description="",
        audio_src="",
        image_src="",
        status="draft:storyline",
    )

    storyline_doc = Storyline(
        creator_id=current_user.uid,
        story_id=story.id,
        plot_outline=storyline["plot_outline"],
        characters=storyline["characters"],
        theme=storyline.get("theme", ""),
        mood=storyline.get("mood", ""),
        tone=storyline.get("tone", ""),
        setting=storyline.get("setting", ""),
        conflict=storyline.get("conflict", ""),
        resolution=storyline.get("resolution", ""),
        moral=storyline.get("moral", ""),
        style=storyline.get("style", ""),
        character_personas={},
    )

    story_metadata_task = asyncio.create_task(
        generate_metadata_for_storyline(storyline, payload.language)
    )

    image_save_path = "./public/posters"
    story_image_task = asyncio.create_task(
        generate_image_for_story(
            storyline.get("plot_outline", ""),
            storyline.get("setting", ""),
            f"{image_save_path}/{story.id}.jpg",
        )
    )

    done, _ = await asyncio.wait(
        [
            story_metadata_task,
            story_image_task,
        ]
    )

    for tr in done:
        resp = tr.result()
        if isinstance(resp, str):
            story.image_src = resp
        else:
            story.title = resp.title
            story.description = resp.description

    db.add_all([story, storyline_doc])
    await db.commit()

    await update_credits_with_transaction(
        db,
        CreateTransactionRequest(
            user_id=current_user.uid,
            amount=CREDIT_NEEDS.STORYLINE,
            remarks="Storyline creation",
            transaction_ref=str(story.id),
        ),
    )
    await update_credits_with_transaction(
        db,
        CreateTransactionRequest(
            user_id=current_user.uid,
            amount=CREDIT_NEEDS.METADATA,
            remarks="Story metadata creation",
            transaction_ref=str(story.id),
        ),
    )

    return {
        "story_id": story.id,
        "storyline": storyline,
    }
