from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import settings as settings_router
from .routers import shows
from .seed import seed_shows

app = FastAPI(title="Personal Podcast Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shows.router)
app.include_router(settings_router.router)
app.mount("/storage", StaticFiles(directory=settings.storage_dir), name="storage")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_shows(db)


@app.get("/api/health")
def health():
    return {"status": "ok"}
