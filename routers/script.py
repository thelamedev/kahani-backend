import logging
from fastapi import APIRouter, HTTPException, Request, status

from modules.script.service import generate_script

router = APIRouter(prefix="/script", tags=["Script"])
logger = logging.getLogger("script.api")


@router.post(
    "",
    description="Create Script with given 'story_outline', 'persona' and 'language'.",
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
