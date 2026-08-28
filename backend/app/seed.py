from sqlalchemy.orm import Session

from .models import AppSetting, Category, CategoryKind

# Voices picked by the user from the ElevenLabs Voice Library (usable directly
# by voice_id even with this restricted key). English premades kept for en mode.
VOICE_JEIJO = {"voice_id": "PBaBRSRTvwmnK1PAq9e0", "voice_name": "JeiJo"}        # es-ES m
VOICE_SANTI = {"voice_id": "Syqs6p4s6hxhfAyhhlbS", "voice_name": "Santi"}        # es-ES m
VOICE_JAVIER_K = {"voice_id": "h415g7h7bSwQrn1qw4ar", "voice_name": "Javier"}    # m, grave
VOICE_MELANIE = {"voice_id": "bN1bDXgDIGX5lw0rtY2B", "voice_name": "Melanie"}    # es-AR f
VOICE_OLIVER = {"voice_id": "FT9r1rAZNP1NDa9qgrTd", "voice_name": "Oliver"}      # LatAm m
VOICE_CHARLIE = {"voice_id": "Yb8JGzcZyW5YYzenhRCm", "voice_name": "Charlie"}    # m, narrador

# Seeded category titles per UI language (slug -> {lang: title}).
CATEGORY_TITLES = {
    "tech": {"es": "Tecnología e IA", "en": "Tech & AI", "ca": "Tecnologia i IA"},
    "finance": {"es": "Finanzas", "en": "Finance", "ca": "Finances"},
    "us": {"es": "Hoy en EE.UU.", "en": "Today in the U.S.", "ca": "Avui als EUA"},
    "colombia": {"es": "Hoy en Colombia", "en": "Today in Colombia", "ca": "Avui a Colòmbia"},
    "spain": {"es": "Hoy en España", "en": "Today in Spain", "ca": "Avui a Espanya"},
    "history": {"es": "Historia", "en": "History", "ca": "Història"},
}

SEED_CATEGORIES = [
    dict(
        slug="tech",
        title="Tecnología e IA",
        position=0,
        interest_prompt=(
            "Noticias de inteligencia artificial: lanzamientos de modelos (p. ej. GLM 5.3 "
            "Flash, herramientas nuevas como Gemini Text-to-Speech), novedades de Anthropic, "
            "OpenAI, Google DeepMind y laboratorios chinos. Me interesa especialmente el "
            "detalle técnico de cómo funcionan los modelos, no solo el anuncio."
        ),
        kind=CategoryKind.news,
        # Single host by default; 2-4 voice dialogue stays supported via this list.
        hosts=[{**VOICE_JEIJO, "persona": "experto técnico que explica con calma cómo funcionan las cosas"}],
    ),
    # Each country row speaks with its own accent — small touch, big demo effect.
    dict(
        slug="finance",
        title="Finanzas",
        position=1,
        interest_prompt=(
            "Noticias financieras y de bolsa: movimientos de mercado, resultados de grandes "
            "tecnológicas, macroeconomía (Fed, BCE), y contexto de por qué se mueve el mercado."
        ),
        kind=CategoryKind.news,
        hosts=[{**VOICE_JAVIER_K, "persona": "analista de mercados sereno, voz grave"}],
    ),
    dict(
        slug="us",
        title="Hoy en EE.UU.",
        position=2,
        interest_prompt=(
            "Actualidad de Estados Unidos: política nacional, decisiones de la Casa Blanca y "
            "el Congreso, sucesos importantes, economía y su impacto internacional."
        ),
        kind=CategoryKind.news,
        hosts=[{**VOICE_MELANIE, "persona": "corresponsal internacional clara y directa"}],
    ),
    dict(
        slug="colombia",
        title="Hoy en Colombia",
        position=3,
        interest_prompt=(
            "Actualidad de Colombia: política nacional, decisiones del gobierno, sucesos "
            "importantes, economía y sociedad."
        ),
        kind=CategoryKind.news,
        hosts=[{**VOICE_OLIVER, "persona": "presentador cercano y riguroso"}],
    ),
    dict(
        slug="spain",
        title="Hoy en España",
        position=4,
        interest_prompt=(
            "Actualidad de España: política nacional, Gobierno y Congreso, comunidades "
            "autónomas, sucesos importantes, economía y relación con la UE."
        ),
        kind=CategoryKind.news,
        hosts=[{**VOICE_JEIJO, "persona": "presentador español directo y claro"}],
    ),
    dict(
        slug="history",
        title="Historia",
        position=5,
        interest_prompt=(
            "Historia: Roma y Grecia antiguas, historia de España (p. ej. la Segunda "
            "República), Segunda Guerra Mundial y siglo XX hasta hoy. Mezcla de curiosidades "
            "(fun facts) y temas contados en profundidad (una guerra entera, una etapa)."
        ),
        kind=CategoryKind.evergreen,
        hosts=[{**VOICE_CHARLIE, "persona": "narrador veterano que cuenta la historia como un cuento"}],
    ),
]


def seed_demo(db: Session) -> None:
    """Seed pre-generated showcase episodes from the committed demo/ bundle.

    The 'demo' category is disabled so it never shows in the home rows or gets
    refreshed by the scheduler — it is served only by /api/demo (Demo tab).
    """
    import json
    import shutil

    from .config import BASE_DIR, settings
    from .models import Episode, Story, StoryStatus

    bundle = BASE_DIR / "demo" / "demo_stories.json"
    if not bundle.exists():
        return
    category = db.query(Category).filter(Category.slug == "demo").first()
    if not category:
        category = Category(
            slug="demo", title="Demo", enabled=False, position=999,
            interest_prompt="Episodios de muestra pregenerados.",
        )
        db.add(category)
        db.flush()

    existing_titles = {s.title for s in category.stories}
    for item in json.loads(bundle.read_text(encoding="utf-8")):
        if item["title"] in existing_titles:
            continue
        audio_src = BASE_DIR / "demo" / item["audio_file"]
        audio_dst = settings.storage_dir / "episodes" / item["audio_file"]
        if audio_src.exists() and not audio_dst.exists():
            shutil.copy2(audio_src, audio_dst)
        story = Story(
            category_id=category.id,
            title=item["title"],
            tagline=item.get("tagline", ""),
            summary=item.get("summary", ""),
            icon=item.get("icon", "🎙️"),
            cover_from=item.get("cover_from", "#1e1b4b"),
            cover_to=item.get("cover_to", "#3b82f6"),
            cover_image=item.get("cover_image"),
            cover_credit=item.get("cover_credit"),
            source_articles=item.get("source_articles", []),
            status=StoryStatus.ready,
            language=item.get("language", "es"),
        )
        db.add(story)
        db.flush()
        db.add(Episode(
            story_id=story.id,
            title=item.get("episode_title", item["title"]),
            script=item.get("script", []),
            audio_path=f"/storage/episodes/{item['audio_file']}",
            duration_s=item.get("duration_s"),
        ))
    db.commit()


def seed_usage_ledger(db: Session) -> None:
    """Restore the real development-time cost ledger on a fresh database.

    Every row is an actually-measured API call from building this product; the
    dashboard's "Live" panel shows them so real unit costs are visible even on
    a fresh clone. Only runs when the ledger is empty (never duplicates).
    """
    import json
    from datetime import datetime

    from .config import BASE_DIR
    from .models import UsageLog

    bundle = BASE_DIR / "demo" / "usage_ledger.json"
    if not bundle.exists() or db.query(UsageLog).first() is not None:
        return
    for row in json.loads(bundle.read_text(encoding="utf-8")):
        db.add(UsageLog(
            kind=row["kind"],
            model=row.get("model", ""),
            meta=row.get("meta", ""),
            input_tokens=row.get("input_tokens", 0),
            output_tokens=row.get("output_tokens", 0),
            characters=row.get("characters", 0),
            cost_usd=row.get("cost_usd", 0.0),
            created_at=datetime.fromisoformat(row["created_at"]),
        ))
    db.commit()


def seed_categories(db: Session) -> None:
    existing = {slug for (slug,) in db.query(Category.slug).all()}
    for data in SEED_CATEGORIES:
        if data["slug"] not in existing:
            db.add(Category(**data))
    if not db.get(AppSetting, 1):
        db.add(AppSetting(id=1, **{f"default_{k}": v for k, v in VOICE_SANTI.items()}))
    db.commit()
