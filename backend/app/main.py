import logging

import truststore

# Use the OS certificate store so HTTPS works behind AV/proxy TLS interception.
# Must run before any httpx/openai/elevenlabs client is created.
truststore.inject_into_ssl()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR, settings
from .database import Base, SessionLocal, engine
from .routers import categories, demo, interests, metrics, settings as settings_router, stories
from .seed import seed_categories, seed_demo

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
app.include_router(interests.router)
app.include_router(metrics.router)
app.include_router(demo.router)
app.mount("/storage", StaticFiles(directory=settings.storage_dir), name="storage")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_categories(db)
        seed_demo(db)
    from . import scheduler

    scheduler.start()


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Production mode: serve the built frontend from the same server, so a
# reviewer runs ONE process and opens ONE url (see run.bat / run.sh).
# Mounted LAST so every /api and /storage route wins over the catch-all.
_frontend_dist = BASE_DIR / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=_frontend_dist, html=True), name="frontend")
