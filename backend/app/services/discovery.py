import logging

from sqlalchemy.orm import Session

from ..models import AppSetting, Category, CategoryKind, Story
from . import llm, sources

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
    existing_titles = [s.title for s in category.stories[:30]]
    lang_rule = language_rule(content_language(db))

    if category.kind == CategoryKind.news:
        articles = sources.fetch_articles(category.slug)
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
        data = llm.chat_json(_DISCOVER_SYSTEM + lang_rule, user)
    else:
        articles = []
        user = (
            f"INTERESES DEL USUARIO:\n{category.interest_prompt}\n\n"
            f"TEMAS YA EXISTENTES (no repetir):\n{existing_titles}"
        )
        data = llm.chat_json(_EVERGREEN_SYSTEM + lang_rule, user)

    created: list[Story] = []
    for item in data.get("stories", []):
        cover_from, cover_to = PALETTES.get(item.get("palette", ""), PALETTES["electrico"])
        backing = [
            {"title": articles[i].title, "url": articles[i].url, "source": articles[i].source}
            for i in item.get("article_indices", [])
            if isinstance(i, int) and 0 <= i < len(articles)
        ]
        story = Story(
            category_id=category.id,
            title=item.get("title", "").strip()[:160],
            tagline=item.get("tagline", "").strip()[:240],
            summary=item.get("summary", "").strip(),
            icon=item.get("icon", "🎙️")[:8],
            cover_from=cover_from,
            cover_to=cover_to,
            source_articles=backing,
        )
        db.add(story)
        created.append(story)
    db.commit()
    return created
