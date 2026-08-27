import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ShowKind(str, enum.Enum):
    news = "news"          # pulls fresh articles inside a time window
    evergreen = "evergreen"  # fun facts / summarized history, no freshness constraint


class EpisodeStatus(str, enum.Enum):
    queued = "queued"
    fetching = "fetching"
    scripting = "scripting"
    tts = "tts"
    ready = "ready"
    failed = "failed"


class Show(Base):
    __tablename__ = "shows"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    tagline: Mapped[str] = mapped_column(String(200), default="")
    # Free-text interest description injected into curation/script prompts.
    interest_prompt: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(40))  # tech | finance | politics | history
    kind: Mapped[ShowKind] = mapped_column(Enum(ShowKind), default=ShowKind.news)

    # CSS cover until image generation lands: gradient stops + icon.
    cover_from: Mapped[str] = mapped_column(String(16), default="#1e3a8a")
    cover_to: Mapped[str] = mapped_column(String(16), default="#0ea5e9")
    cover_icon: Mapped[str] = mapped_column(String(16), default="🎙️")
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # List of hosts: [{"voice_id": ..., "voice_name": ..., "persona": ...}, ...].
    # Empty list -> single host using the app-wide default voice.
    # 2+ hosts -> the script is generated as a dialogue between them.
    hosts: Mapped[list] = mapped_column(JSON, default=list)

    enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    episodes: Mapped[list["Episode"]] = relationship(
        back_populates="show", cascade="all, delete-orphan", order_by="Episode.id.desc()"
    )


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    show_id: Mapped[int] = mapped_column(ForeignKey("shows.id"))
    title: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[EpisodeStatus] = mapped_column(
        Enum(EpisodeStatus), default=EpisodeStatus.queued
    )
    script: Mapped[str] = mapped_column(Text, default="")
    audio_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    show: Mapped[Show] = relationship(back_populates="episodes")


class AppSetting(Base):
    """Single-row app-wide settings (default narrator voice, etc.)."""

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    default_voice_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    default_voice_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
