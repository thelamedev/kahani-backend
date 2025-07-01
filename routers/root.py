from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, status

from modules.storyline.service import generate_story_outline
from modules.persona.service import generate_character_person
from modules.script.service import generate_script
from modules.voice.service import generate_voice_for_script
from routers.dtos.storyline import StorylineRequestPayload

router = APIRouter(tags=["Root"])
bootup_time = datetime.now()


@router.get("/health")
async def health_check():
    uptime = datetime.now() - bootup_time
    return {"status": "Healthy", "uptime": f"{uptime}"}
