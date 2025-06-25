from typing import Any, Dict, List
from sqlalchemy import UUID, Column, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from shared.database import Base


class Story(Base):
    __tablename__ = "stories"

    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user_input = Column(String)
    language: Mapped[str] = mapped_column(String)

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    audio_src: Mapped[str] = mapped_column(String)
    image_src: Mapped[str] = mapped_column(String)

    # NOTE: This will be an enum on application layer for now
    status: Mapped[str] = mapped_column(String)


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
    character_personas: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)


class Script(Base):
    __tablename__ = "scripts"

    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    story_id = Column(UUID(as_uuid=True), ForeignKey("stories.id"))

    dialogues: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
