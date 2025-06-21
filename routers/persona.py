import logging
from fastapi import APIRouter, HTTPException, Request, status

from modules.persona.service import generate_character_person

router = APIRouter(prefix="/persona", tags=["Persona"])
logger = logging.getLogger("persona.api")


@router.post(
    "",
    description="Create character persona. Expects story outline in the body as is.",
)
async def request_persona_generation(req: Request):
    body = await req.json()

    if not body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "empty request body")

    persona = await generate_character_person(body)

    return persona
