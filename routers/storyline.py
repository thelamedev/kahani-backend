import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status

from modules.storyline.service import generate_story_outline
from shared.auth_middleware import AuthUser, get_current_user
from shared.database import AsyncSession, get_db
from shared.models.story import Story, Storyline

router = APIRouter(prefix="/storyline", tags=["Storyline"])
logger = logging.getLogger("storyline.api")


@router.post(
    "",
    description="Create Storyline with given 'user_input'.",
    deprecated=True,
)
async def request_storyline_generation(
    req: Request,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    body = await req.json()

    user_input = body.get("user_input")
    language = body.get("language")

    if not user_input:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    storyline = await generate_story_outline(user_input)

    story = Story(
        id=uuid.uuid4(),
        creator_id=current_user.uid,
        user_input=user_input,
        language=language,
        title="",
        description="",
        audio_src="",
        image_src="",
        status="progress:storyline",
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
