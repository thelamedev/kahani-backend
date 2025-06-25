from sqlalchemy import UUID, Column, ForeignKey, String, JSON
from shared.database import Base


class Story(Base):
    __tablename__ = "stories"

    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user_input = Column(String)
    language = Column(String)

    title = Column(String)
    description = Column(String)
    audio_src = Column(String)
    image_src = Column(String)

    # NOTE: This will be an enum on application layer for now
    status = Column(String)


class Storyline(Base):
    __tablename__ = "storylines"

    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id"))

    plot_outline = Column(String, nullable=False)
    characters = Column(JSON, nullable=False)
    theme = Column(String)
    mood = Column(String)
    tone = Column(String)
    setting = Column(String)
    conflict = Column(String)
    resolution = Column(String)
    moral = Column(String)
    style = Column(String)
    character_personas = Column(JSON)


class Script(Base):
    __tablename__ = "scripts"

    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id"))

    dialogues = Column(JSON)
