import logging
from typing import Annotated
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, status

from modules.metadata.service import generate_metadata_for_storyline
from modules.storyline.service import generate_story_outline
from routers.dtos.storyline import StorylineRequestPayload
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import AsyncSession, get_db
from shared.models.story import Story, Storyline

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

    storyline = await generate_story_outline(payload.user_input)
    story_metadata = await generate_metadata_for_storyline(storyline, payload.language)

    story = Story(
        id=uuid.uuid4(),
        creator_id=current_user.uid,
        user_input=payload.user_input,
        language=payload.language,
        title=story_metadata.title,
        description=story_metadata.description,
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

    db.add_all([story, storyline_doc])
    await db.commit()

    return {
        "story_id": story.id,
        "storyline": storyline,
    }
