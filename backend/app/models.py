import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CategoryKind(str, enum.Enum):
    news = "news"          # stories discovered from fresh articles
    evergreen = "evergreen"  # stories proposed by the LLM (history, fun facts)


class StoryStatus(str, enum.Enum):
    suggested = "suggested"   # card exists, no audio yet
    generating = "generating"
    ready = "ready"
    failed = "failed"


class Category(Base):
    """A home-page row: 'Hoy en EE.UU.', 'Tecnología e IA', ..."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    interest_prompt: Mapped[str] = mapped_column(Text, default="")
    kind: Mapped[CategoryKind] = mapped_column(Enum(CategoryKind), default=CategoryKind.news)

    # Hosts for this category's episodes:
    # [{"voice_id":..., "voice_name":..., "persona":...}, ...]
    # Empty -> single host with the app-wide default voice.
    hosts: Mapped[list] = mapped_column(JSON, default=list)

    enabled: Mapped[bool] = mapped_column(default=True)
    position: Mapped[int] = mapped_column(default=0)

    stories: Mapped[list["Story"]] = relationship(
        back_populates="category", cascade="all, delete-orphan", order_by="Story.id.desc()"
    )


class Story(Base):
    """One card in a row: a concrete news story or evergreen topic."""

    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    title: Mapped[str] = mapped_column(String(160))
    tagline: Mapped[str] = mapped_column(String(240), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(16), default="🎙️")
    cover_from: Mapped[str] = mapped_column(String(16), default="#4c1d95")
    cover_to: Mapped[str] = mapped_column(String(16), default="#2563eb")
    # og:image of the top backing article (news-aggregator style thumbnail),
    # else a CC-licensed image from Openverse (cover_credit holds attribution);
    # the gradient poster is the last-resort fallback.
    cover_image: Mapped[str | None] = mapped_column(String(600), nullable=True)
    cover_credit: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # Editions are cached per language: switching back to an already-generated
    # language is instant and free (the UI filters by the active language).
    language: Mapped[str] = mapped_column(String(8), default="es")
    # Articles backing this story: [{"title":..., "url":..., "source":...}, ...]
    source_articles: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[StoryStatus] = mapped_column(Enum(StoryStatus), default=StoryStatus.suggested)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category: Mapped[Category] = relationship(back_populates="stories")
    episodes: Mapped[list["Episode"]] = relationship(
        back_populates="story", cascade="all, delete-orphan", order_by="Episode.id.desc()"
    )


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    title: Mapped[str] = mapped_column(String(200), default="")
    # Script as dialogue lines: [{"host": 0, "text": "..."}, ...] (host 0 only for mono)
    script: Mapped[list] = mapped_column(JSON, default=list)
    audio_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    story: Mapped[Story] = relationship(back_populates="episodes")


class UsageLog(Base):
    """Real-cost ledger: one row per LLM/TTS call. Feeds the dashboard."""

    __tablename__ = "usage_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(24))  # curation | script | tts | transcribe
    model: Mapped[str] = mapped_column(String(64), default="")
    meta: Mapped[str] = mapped_column(String(120), default="")  # e.g. category slug
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    characters: Mapped[int] = mapped_column(Integer, default=0)  # TTS
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AppSetting(Base):
    """Single-row app-wide settings (default narrator voice, etc.)."""

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    default_voice_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    default_voice_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Podcast + UI language: es (default, fits ONDA) | en | ca
    language: Mapped[str] = mapped_column(String(8), default="es")
