import concurrent.futures
import logging

from sqlalchemy.orm import Session

from ..models import AppSetting, Category, CategoryKind, Story
from . import images, llm, sources

log = logging.getLogger(__name__)

# Podcast content language (cards + scripts). UI copy stays as-is.
LANGUAGES = {"en": "inglés (English)", "es": "español", "ca": "catalán (català)"}


def content_language(db: Session) -> str:
    setting = db.get(AppSetting, 1)
    return setting.language if setting and setting.language in LANGUAGES else "en"


def language_rule(lang: str) -> str:
    return (
        f"\n\nIDIOMA DE SALIDA: escribe title, tagline y summary en {LANGUAGES[lang]}, "
        "aunque los artículos estén en otro idioma."
    )

# Poster palettes the model picks from — cool, deep tones as the base identity,
# warm ones reserved for stories that call for them.
PALETTES = {
    "medianoche": ("#1e1b4b", "#3b82f6"),
    "electrico": ("#312e81", "#06b6d4"),
    "purpura": ("#4c1d95", "#8b5cf6"),
    "oceano": ("#0c4a6e", "#38bdf8"),
    "esmeralda": ("#064e3b", "#34d399"),
    "acero": ("#1e293b", "#94a3b8"),
    "vino": ("#4a044e", "#a21caf"),
    "oro": ("#713f12", "#f59e0b"),
    "magma": ("#7c2d12", "#ea580c"),
    "sangre": ("#7f1d1d", "#ef4444"),
}

_DISCOVER_SYSTEM = """Eres el editor jefe de un servicio de podcasts personalizados.
Recibes una lista numerada de artículos recientes y debes agruparlos en HISTORIAS concretas
para tarjetas tipo Netflix. Una historia = un acontecimiento o tema específico (no una
categoría genérica). Prioriza lo más relevante para los intereses del usuario.

Devuelve JSON con esta forma exacta:
{"stories": [{
  "title": "titular corto y con gancho (máx 8 palabras)",
  "tagline": "subtítulo de una frase que dé contexto",
  "summary": "resumen de 3-4 frases con los hechos clave",
  "icon": "un emoji que represente la historia",
  "palette": "una de: medianoche, electrico, purpura, oceano, esmeralda, acero, vino, oro, magma, sangre (prefiere las frías: medianoche, electrico, purpura, oceano, esmeralda, acero; usa cálidas solo si la historia lo pide)",
  "article_indices": [índices de los artículos que respaldan esta historia]
}]}

Reglas: entre 6 y 8 historias, variadas entre sí y con paletas variadas. No repitas
historias ya existentes (se te da la lista). Si varios artículos cubren lo mismo,
agrúpalos en una sola historia."""

_EVERGREEN_SYSTEM = """Eres el editor de un podcast de historia. Propón temas para
tarjetas tipo Netflix según los intereses del usuario. Mezcla dos formatos: "fun facts"
(curiosidades sorprendentes) e "historia en profundidad" (una guerra, una etapa, contada entera).

Devuelve JSON con esta forma exacta:
{"stories": [{
  "title": "título corto y con gancho (máx 8 palabras)",
  "tagline": "subtítulo de una frase",
  "summary": "resumen de 3-4 frases de lo que cubriría el episodio",
  "icon": "un emoji",
  "palette": "una de: medianoche, electrico, purpura, oceano, esmeralda, acero, vino, oro, magma, sangre (prefiere las frías: medianoche, electrico, purpura, oceano, esmeralda, acero; usa cálidas solo si la historia lo pide)",
  "article_indices": []
}]}

Reglas: exactamente 8 temas, ninguno repetido con los ya existentes, mezcla épocas y formatos."""


def discover(db: Session, category: Category) -> list[Story]:
    lang = content_language(db)
    existing_titles = [s.title for s in category.stories if s.language == lang][:30]
    lang_rule = language_rule(lang)

    if category.kind == CategoryKind.news:
        articles = sources.fetch_articles(category.slug, query=category.title, lang=lang)
        if not articles:
            raise RuntimeError("Ninguna fuente devolvió artículos")
        listing = "\n".join(
            f"{i}. [{a.source}] {a.title} — {a.summary[:160]}" for i, a in enumerate(articles)
        )
        user = (
            f"INTERESES DEL USUARIO:\n{category.interest_prompt}\n\n"
            f"HISTORIAS YA EXISTENTES (no repetir):\n{existing_titles}\n\n"
            f"ARTÍCULOS:\n{listing}"
        )
        data = llm.chat_json(_DISCOVER_SYSTEM + lang_rule, user, kind="curation", meta=category.slug)
    else:
        articles = []
        user = (
            f"INTERESES DEL USUARIO:\n{category.interest_prompt}\n\n"
            f"TEMAS YA EXISTENTES (no repetir):\n{existing_titles}"
        )
        data = llm.chat_json(_EVERGREEN_SYSTEM + lang_rule, user, kind="curation", meta=category.slug)

    created: list[Story] = []
    for item in data.get("stories", []):
        cover_from, cover_to = PALETTES.get(item.get("palette", ""), PALETTES["electrico"])
        backing_articles = [
            articles[i]
            for i in item.get("article_indices", [])
            if isinstance(i, int) and 0 <= i < len(articles)
        ]
        backing = [
            {"title": a.title, "url": a.url, "source": a.source} for a in backing_articles
        ]
        # Fast cover only (RSS image, no HTTP): cards must appear immediately.
        # Slower lookups (og:image, Openverse) run in parallel right after.
        cover_image = next((a.image for a in backing_articles if a.image), None)
        story = Story(
            category_id=category.id,
            title=item.get("title", "").strip()[:160],
            tagline=item.get("tagline", "").strip()[:240],
            summary=item.get("summary", "").strip(),
            icon=item.get("icon", "🎙️")[:8],
            cover_from=cover_from,
            cover_to=cover_to,
            cover_image=cover_image,
            source_articles=backing,
            language=lang,
        )
        db.add(story)
        created.append(story)

    # Commit NOW: cards show up in the UI at once (gradient poster), images
    # stream in progressively via the polling refresh.
    db.commit()

    # Every card gets a real photo: og:image of a backing article, else a
    # CC-licensed Openverse photo (queries minted in one cheap LLM batch call).
    # All network lookups run in parallel — this was the slow part.
    missing = [(i, s.title, s.tagline) for i, s in enumerate(created) if not s.cover_image]
    if missing:
        queries = images.image_queries(missing)
        fallback_query = images.CATEGORY_FALLBACK_QUERIES.get(category.slug, category.title)

        def find_cover(index: int) -> tuple[int, tuple[str, str] | None]:
            story = created[index]
            for a in (story.source_articles or [])[:2]:
                og = sources.fetch_og_image(a["url"])
                if og:
                    return index, (og, "")
            query = queries.get(index)
            result = images.search_free_image(query) if query else None
            return index, (result or images.search_free_image(fallback_query))

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for index, result in pool.map(find_cover, [i for i, _, _ in missing]):
                if result:
                    created[index].cover_image, created[index].cover_credit = result
        db.commit()

    return created
