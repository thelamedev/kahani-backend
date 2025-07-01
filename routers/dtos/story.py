from pydantic import BaseModel, Field, field_validator


class UpdateStoryPayload(BaseModel):
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    image_src: str | None = Field(default=None)
    visibility: str | None = Field(default=None)

    @field_validator("visibility")
    def validate_field_1(cls, v):
        if v is None:
            return v
        if v in ["private", "public"]:
            return v
        raise ValueError(f"unknown value for visibility: '{v}'")
