from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import EpisodeStatus, ShowKind


class Host(BaseModel):
    voice_id: str
    voice_name: str
    persona: str = ""  # e.g. "presentadora escéptica", "experto entusiasta"


class EpisodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    show_id: int
    title: str
    status: EpisodeStatus
    audio_path: str | None
    duration_s: float | None
    created_at: datetime


class ShowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    tagline: str
    interest_prompt: str
    category: str
    kind: ShowKind
    cover_from: str
    cover_to: str
    cover_icon: str
    cover_image: str | None
    hosts: list[Host]
    enabled: bool


class ShowUpdate(BaseModel):
    title: str | None = None
    tagline: str | None = None
    interest_prompt: str | None = None
    hosts: list[Host] | None = Field(default=None, max_length=4)
    enabled: bool | None = None


class AppSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    default_voice_id: str | None
    default_voice_name: str | None


class AppSettingsUpdate(BaseModel):
    default_voice_id: str | None = None
    default_voice_name: str | None = None
