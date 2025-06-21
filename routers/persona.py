import logging
from fastapi import APIRouter, HTTPException, Request, status

from modules.persona.service import generate_character_person

router = APIRouter(prefix="/persona")
logger = logging.getLogger("persona.api")


@router.post("")
async def request_persona_generation(req: Request):
    body = await req.json()

    if not body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "empty request body")

    persona = await generate_character_person(body)

    return persona
