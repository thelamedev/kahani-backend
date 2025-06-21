import logging
from fastapi import APIRouter, HTTPException, Request, status

from modules.voice.service import generate_voice_for_script
from shared.language_codes import LANGUAGE_CODES

router = APIRouter(prefix="/voice", tags=["Voice"])
logger = logging.getLogger("voice.api")


@router.post(
    "",
    description="Create Voice with given 'script', 'persona' and 'language'.",
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
