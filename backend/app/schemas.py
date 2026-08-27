from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import CategoryKind, StoryStatus


class Host(BaseModel):
    voice_id: str
    voice_name: str
    persona: str = ""


class EpisodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    story_id: int
    title: str
    script: list[dict]
    audio_path: str | None
    duration_s: float | None
    error: str | None
    created_at: datetime


class StoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    title: str
    tagline: str
    summary: str
    icon: str
    cover_from: str
    cover_to: str
    cover_image: str | None
    cover_credit: str | None
    source_articles: list[dict]
    status: StoryStatus
    created_at: datetime


class StoryDetail(StoryOut):
    episodes: list[EpisodeOut]


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    interest_prompt: str
    kind: CategoryKind
    hosts: list[Host]
    enabled: bool
    position: int


class CategoryUpdate(BaseModel):
    title: str | None = None
    interest_prompt: str | None = None
    hosts: list[Host] | None = Field(default=None, max_length=4)
    enabled: bool | None = None


class AppSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    default_voice_id: str | None
    default_voice_name: str | None
    language: str


class AppSettingsUpdate(BaseModel):
    default_voice_id: str | None = None
    default_voice_name: str | None = None
    language: str | None = Field(default=None, pattern="^(en|es|ca)$")
