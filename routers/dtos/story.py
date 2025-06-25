from pydantic import BaseModel, Field


class UpdateStoryPayload(BaseModel):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    image_src: str | None = Field(default=None)
