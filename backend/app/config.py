from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    gemini_api_key: str = ""

    # Curation (news clustering) — structured JSON work on the cheap tier.
    openai_model: str = "gpt-5.6-luna"
    # Scriptwriting — GPT-5.6 Sol: best OpenAI writer on EQ-Bench Creative
    # Writing (Aug 2026; overall #1 is Claude Opus 5, no key available).
    script_provider: str = "openai"
    script_model: str = "gpt-5.6-sol"
    gemini_model: str = "gemini-3.7-flash"

    elevenlabs_model: str = "eleven_multilingual_v2"
    episode_target_words: int = 800  # ~5 min at spoken pace

    # Postgres in docker-compose; SQLite fallback for machines without it.
    database_url: str = f"sqlite:///{BASE_DIR / 'storage' / 'podcast.db'}"

    storage_dir: Path = BASE_DIR / "storage"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
(settings.storage_dir / "episodes").mkdir(exist_ok=True)


# USD per million tokens (input, output) — for the real-cost ledger.
MODEL_PRICES = {
    "gpt-5.1": (1.25, 10.0),
    "gpt-5.5": (5.0, 30.0),
    "gpt-5.6-sol": (5.0, 30.0),
    "gpt-5.6-terra": (2.5, 15.0),
    "gpt-5.6-luna": (1.0, 6.0),
    "gemini-3.7-flash": (0.5, 3.0),
}
# ElevenLabs multilingual v2, approx USD per 1k characters.
TTS_PRICE_PER_1K_CHARS = 0.18
