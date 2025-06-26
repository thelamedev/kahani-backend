from pydantic import BaseModel


class StorylineRequestPayload(BaseModel):
    user_input: str
    language: str
