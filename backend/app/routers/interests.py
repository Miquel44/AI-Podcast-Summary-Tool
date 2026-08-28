import io
import logging
import threading
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, CategoryKind
from ..services import llm

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interests", tags=["interests"])

# Topics offered beyond the pre-generated (recommended) ones. Creating one
# spins up a dynamic category fed by Google News, so the UI warns about
# regeneration cost before applying.
EXTRA_TOPICS = [
    "Deportes", "Fútbol", "Fórmula 1", "Ciencia", "Espacio", "Cine y series",
    "Música", "Videojuegos", "Criptomonedas", "Startups", "Salud",
    "Medio ambiente", "Gastronomía", "Viajes",
]


def slugify(name: str) -> str:
    norm = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "-".join(norm.lower().split())[:64]


class AnalyzeIn(BaseModel):
    text: str


class ApplyIn(BaseModel):
    topics: list[str]


_TAGS_SYSTEM = """Extraes intereses de una descripción libre de un usuario para un
servicio de podcasts de noticias. Devuelve JSON: {"tags": ["...", ...]}.
Reglas: entre 2 y 8 tags, cada uno de 1-3 palabras, en el idioma del usuario,
concretos y útiles como tema de noticias (p. ej. "Fórmula 1", no "cosas de coches")."""


@router.get("/suggestions")
def suggestions(db: Session = Depends(get_db)):
    categories = (
        db.query(Category)
        .filter(Category.slug != "demo")  # showcase shelf, not a pickable interest
        .order_by(Category.position, Category.id)
        .all()
    )
    return {
        "recommended": [
            {"slug": c.slug, "title": c.title, "enabled": c.enabled} for c in categories
        ],
        "extra": EXTRA_TOPICS,
    }


@router.post("/analyze")
def analyze_text(payload: AnalyzeIn):
    if not payload.text.strip():
        raise HTTPException(422, "Texto vacío")
    data = llm.chat_json(_TAGS_SYSTEM, payload.text)
    return {"tags": [str(t)[:40] for t in data.get("tags", [])][:8]}


@router.post("/analyze-audio")
async def analyze_audio(file: UploadFile):
    raw = await file.read()
    if not raw:
        raise HTTPException(422, "Audio vacío")
    buffer = io.BytesIO(raw)
    buffer.name = file.filename or "audio.ogg"
    transcript = llm.client().audio.transcriptions.create(
        model="gpt-4o-transcribe", file=buffer
    )
    data = llm.chat_json(_TAGS_SYSTEM, transcript.text)
    return {"transcript": transcript.text, "tags": [str(t)[:40] for t in data.get("tags", [])][:8]}


@router.post("/apply")
def apply(payload: ApplyIn, db: Session = Depends(get_db)):
    """Enable/create categories to match the selected topics; disable the rest."""
    if not payload.topics:
        raise HTTPException(422, "Selecciona al menos un tema")

    selected = {slug: t for t in payload.topics if (slug := slugify(t))}
    if not selected:
        raise HTTPException(422, "Ningún tema válido")

    all_categories = db.query(Category).all()
    by_slug = {c.slug: c for c in all_categories}
    # The UI selects by display title while seeded categories use short slugs
    # ("Tecnología e IA" -> "tech"), so match by slugified title as well.
    by_title = {slugify(c.title): c for c in all_categories}

    created, kept_slugs = [], set()
    max_pos = max((c.position for c in all_categories), default=0)
    for slug, name in selected.items():
        category = by_slug.get(slug) or by_title.get(slug)
        if category:
            category.enabled = True
            kept_slugs.add(category.slug)
        else:
            max_pos += 1
            db.add(Category(
                slug=slug,
                title=name,
                interest_prompt=f"Noticias y actualidad sobre {name}.",
                kind=CategoryKind.news,
                position=max_pos,
            ))
            created.append(name)
    for category in all_categories:
        if category.slug not in kept_slugs and category.slug != "demo":
            category.enabled = False
    db.commit()

    # Fill the new/empty rows in the background (fresh rows are skipped).
    from .. import scheduler

    threading.Thread(target=scheduler.refresh_all, daemon=True).start()
    return {"created": created, "enabled": sorted(selected)}
