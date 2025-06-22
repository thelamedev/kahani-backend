from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, status

from modules.storyline.service import generate_story_outline
from modules.persona.service import generate_character_person
from modules.script.service import generate_script
from modules.voice.service import generate_voice_for_script

router = APIRouter(tags=["Root"])
bootup_time = datetime.now()


@router.get("/health")
async def health_check():
    uptime = datetime.now() - bootup_time
    return {"status": "Healthy", "uptime": f"{uptime}"}


@router.post("/quick-generate")
async def quick_generate_story_and_audio(
    user_input: Annotated[str, Body()],
    language: Annotated[str, Body()],
):
    if not user_input:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'user_input' is required")

    if not language:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'language' is required")

    print("Generating story")
    story_outline = await generate_story_outline(user_input)

    print("Generating persona")
    persona = await generate_character_person(story_outline)

    print("Generating script")
    script_response = await generate_script(story_outline, persona, language)

    print("Generating voices")
    voice_path = await generate_voice_for_script(
        script_response,
        persona,
        language,
    )

    return {"audio_path": voice_path}
