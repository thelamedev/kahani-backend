from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from shared.database import engine
from shared.models import Base

from routers.root import router as root_router
from routers.storyline import router as storyline_router
from routers.persona import router as persona_router
from routers.script import router as script_router
from routers.voice import router as voice_router
from routers.auth import router as auth_router
from routers.story import router as story_router
from routers.clerk_webhook import router as clerk_router
from routers.transactions import router as transaction_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        async with engine.begin() as conn:
            print("Running SQLAlchemy Engine Migrations...")
            await conn.run_sync(Base.metadata.create_all)

        yield
    finally:
        print("Disposing SqlAlchemy Engine")
        await engine.dispose()


api = APIRouter(prefix="/api/v1")

api.include_router(root_router)
api.include_router(persona_router)
api.include_router(storyline_router)
api.include_router(script_router)
api.include_router(voice_router)
api.include_router(auth_router)
api.include_router(story_router)
api.include_router(clerk_router)
api.include_router(transaction_router)

app = FastAPI(
    lifespan=lifespan,
    title="Kahani API",
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

app.mount("/public", StaticFiles(directory="public"), name="public")
