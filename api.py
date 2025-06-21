from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from shared.database import close_database, connect_database

from routers.root import router as root_router
from routers.storyline import router as storyline_router
from routers.persona import router as persona_router
from routers.script import router as script_router
from routers.voice import router as voice_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        connect_database()

        yield
    finally:
        close_database()


api = APIRouter(prefix="/api/v1")

api.include_router(root_router)
api.include_router(persona_router)
api.include_router(storyline_router)
api.include_router(script_router)
api.include_router(voice_router)

app = FastAPI(
    lifespan=lifespan,
    title="Kahani",
    summary="Kahani is a multi-agentic system for creating immersive audio-only stories based on user prompts. ",
    version="1.0.1",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api)
