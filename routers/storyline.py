import logging
from fastapi import APIRouter, HTTPException, Request, status

from modules.storyline.service import generate_story_outline

router = APIRouter(prefix="/storyline", tags=["Storyline"])
logger = logging.getLogger("storyline.api")


@router.post(
    "",
    description="Create Storyline with given 'user_input'.",
)
async def request_storyline_generation(req: Request):
    body = await req.json()

    user_input = body.get("user_input")

    if not user_input:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    storyline = await generate_story_outline(user_input)

    return storyline
