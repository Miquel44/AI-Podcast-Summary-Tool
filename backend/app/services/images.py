"""Free-use cover images via the Openverse API (CC-licensed, no key needed).

Used when no backing article provides an og:image, so every card gets a real
photo. Attribution (creator + license) is stored and shown in the story modal.
"""

import logging

import httpx

log = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "personal-podcast-generator (take-home demo)"}


def search_free_image(query: str) -> tuple[str, str] | None:
    """Returns (image_url, attribution) or None. Commercial-use CC only."""
    try:
        resp = httpx.get(
            "https://api.openverse.org/v1/images/",
            params={
                "q": query,
                "page_size": 8,
                "license_type": "commercial",
                "mature": "false",
            },
            timeout=12,
            headers=_HEADERS,
        )
        resp.raise_for_status()
        for item in resp.json().get("results", []):
            width = item.get("width") or 0
            title = (item.get("title") or "").lower()
            if width < 640 or "placeholder" in title:
                continue
            url = item.get("url", "")
            if not url.startswith("http"):
                continue
            creator = item.get("creator") or "autor desconocido"
            license_name = (item.get("license") or "cc").upper()
            credit = f"Foto: {creator} · CC {license_name} (Openverse)"
            return url[:600], credit[:300]
    except Exception as exc:
        log.warning("openverse search failed for %r: %s", query, exc)
    return None


# Generic per-category queries used when the story-specific search finds
# nothing (Openverse can come back empty for narrow queries).
CATEGORY_FALLBACK_QUERIES = {
    "tech": "technology circuit board",
    "finance": "financial district skyline",
    "us": "washington dc capitol",
    "colombia": "bogota colombia city",
    "spain": "madrid spain city",
    "history": "ancient history ruins",
}


_QUERY_SYSTEM = """Para cada historia de podcast se necesita una consulta de búsqueda de
FOTO de archivo en inglés (2-4 palabras, visual y genérica: lugares, objetos,
escenas — nunca nombres de personas ni marcas). Devuelve JSON:
{"queries": {"<índice>": "<consulta en inglés>", ...}}"""


def image_queries(items: list[tuple[int, str, str]]) -> dict[int, str]:
    """LLM-batch: [(index, title, tagline)] -> {index: english stock-photo query}."""
    from . import llm

    listing = "\n".join(f"{i}. {title} — {tagline}" for i, title, tagline in items)
    try:
        data = llm.chat_json(_QUERY_SYSTEM, listing, kind="curation", meta="image-queries")
        return {
            int(k): str(v)[:80]
            for k, v in data.get("queries", {}).items()
            if str(v).strip()
        }
    except Exception as exc:
        log.warning("image query generation failed: %s", exc)
        return {}
