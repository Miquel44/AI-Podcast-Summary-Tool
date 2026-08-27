import logging

import truststore

# Use the OS certificate store so HTTPS works behind AV/proxy TLS interception.
# Must run before any httpx/openai/elevenlabs client is created.
truststore.inject_into_ssl()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import categories, settings as settings_router, stories
from .seed import seed_categories

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Personal Podcast Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(stories.router)
app.include_router(settings_router.router)
app.mount("/storage", StaticFiles(directory=settings.storage_dir), name="storage")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_categories(db)
    from . import scheduler

    scheduler.start()


@app.get("/api/health")
def health():
    return {"status": "ok"}
