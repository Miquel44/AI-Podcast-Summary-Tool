"""Per-category news sources and the resilient fetcher.

Google News RSS (per-query, per-country) is the freshness backbone — the
closest legal equivalent to "Twitter speed" — complemented by native outlets.
A dead feed is skipped, never fatal.
"""

import concurrent.futures
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import feedparser
import httpx

log = logging.getLogger(__name__)


def gnews(query: str, hl: str, gl: str) -> str:
    return (
        f"https://news.google.com/rss/search?q={quote(query)}"
        f"&hl={hl}&gl={gl}&ceid={gl}:{hl}"
    )


FEEDS: dict[str, list[dict]] = {
    "tech": [
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage?points=100"},
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "Google News · IA", "url": gnews("inteligencia artificial OR OpenAI OR Anthropic OR Gemini", "es", "ES")},
    ],
    "finance": [
        {"name": "CNBC Markets", "url": "https://www.cnbc.com/id/20910258/device/rss/rss.html"},
        {"name": "MarketWatch", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
        {"name": "Financial Times", "url": "https://www.ft.com/rss/home"},
        {"name": "Google News · Mercados", "url": gnews("bolsa mercados wall street", "es", "ES")},
    ],
    "us": [
        {"name": "NPR Politics", "url": "https://feeds.npr.org/1014/rss.xml"},
        {"name": "NYT Politics", "url": "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"},
        {"name": "Politico", "url": "https://rss.politico.com/politics-news.xml"},
        {"name": "Google News · EE.UU.", "url": gnews("Estados Unidos", "es-419", "US")},
    ],
    "colombia": [
        {"name": "El Tiempo", "url": "https://www.eltiempo.com/rss/politica.xml"},
        {"name": "El Espectador", "url": "https://www.elespectador.com/arc/outboundfeeds/rss/category/politica/?outputType=xml"},
        {"name": "Google News · Colombia", "url": gnews("Colombia", "es-419", "CO")},
    ],
    "spain": [
        {"name": "El País", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"},
        {"name": "20minutos", "url": "https://www.20minutos.es/rss/"},
        {"name": "Google News · España", "url": gnews("España", "es", "ES")},
    ],
    # "history" is evergreen: no feeds, the LLM proposes topics.
}


@dataclass
class Article:
    title: str
    url: str
    source: str
    summary: str
    published: datetime | None
    image: str | None = None


def _entry_image(entry) -> str | None:
    """Best image URL a feed entry carries (media RSS, thumbnail, enclosure)."""
    for media in getattr(entry, "media_content", []) or []:
        url = media.get("url", "")
        if url and media.get("medium", "image") == "image":
            return url
    for thumb in getattr(entry, "media_thumbnail", []) or []:
        if thumb.get("url"):
            return thumb["url"]
    for enc in getattr(entry, "enclosures", []) or []:
        if enc.get("href") and "image" in enc.get("type", ""):
            return enc["href"]
    return None


def _fetch_one(source: dict, timeout: float = 10.0) -> list[Article]:
    try:
        resp = httpx.get(
            source["url"],
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (personal-podcast-generator)"},
        )
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        articles = []
        for entry in feed.entries[:25]:
            published = None
            for key in ("published_parsed", "updated_parsed"):
                t = getattr(entry, key, None)
                if t:
                    published = datetime(*t[:6], tzinfo=timezone.utc)
                    break
            articles.append(
                Article(
                    title=getattr(entry, "title", "").strip(),
                    url=getattr(entry, "link", ""),
                    source=source["name"],
                    summary=getattr(entry, "summary", "")[:500],
                    published=published,
                    image=_entry_image(entry),
                )
            )
        return articles
    except Exception as exc:  # a broken feed must never kill discovery
        log.warning("source %s failed: %s", source["name"], exc)
        return []


# Locale for Google News per content language.
GNEWS_LOCALE = {"es": ("es", "ES"), "en": ("en", "US"), "ca": ("ca", "ES")}


def fetch_articles(
    category_slug: str,
    query: str | None = None,
    lang: str = "es",
    window_hours: int = 36,
    cap: int = 60,
) -> list[Article]:
    sources = FEEDS.get(category_slug, [])
    if not sources and query:
        # Dynamic category (user-created interest): Google News is the backbone.
        hl, gl = GNEWS_LOCALE.get(lang, GNEWS_LOCALE["es"])
        sources = [{"name": f"Google News · {query}", "url": gnews(query, hl, gl)}]
    if not sources:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as pool:
        results = pool.map(_fetch_one, sources)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    seen_urls: set[str] = set()
    articles: list[Article] = []
    for batch in results:
        for a in batch:
            if not a.title or a.url in seen_urls:
                continue
            if a.published and a.published < cutoff:
                continue
            seen_urls.add(a.url)
            articles.append(a)

    articles.sort(key=lambda a: a.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return articles[:cap]


_OG_IMAGE_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']'
    r'|<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image["\']',
    re.IGNORECASE,
)


def fetch_og_image(url: str, timeout: float = 4.0) -> str | None:
    """og:image of an article page. Google News redirect pages are skipped."""
    if "news.google.com" in url:
        return None
    try:
        resp = httpx.get(
            url, timeout=timeout, follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (personal-podcast-generator)"},
        )
        resp.raise_for_status()
        match = _OG_IMAGE_RE.search(resp.text[:60_000])
        if match:
            image = (match.group(1) or match.group(2) or "").strip()
            return image[:600] if image.startswith("http") else None
    except Exception as exc:
        log.debug("og:image failed for %s: %s", url, exc)
    return None
