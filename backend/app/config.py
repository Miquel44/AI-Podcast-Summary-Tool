from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: str = ""
    elevenlabs_api_key: str = ""

    # Postgres in docker-compose; SQLite fallback for machines without it.
    database_url: str = f"sqlite:///{BASE_DIR / 'storage' / 'podcast.db'}"

    storage_dir: Path = BASE_DIR / "storage"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
(settings.storage_dir / "episodes").mkdir(exist_ok=True)
