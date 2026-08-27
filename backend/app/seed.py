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
VOICE_RACHEL = {"voice_id": "21m00Tcm4TlvDq8ikWAM", "voice_name": "Rachel"}      # en f
VOICE_ADAM = {"voice_id": "pNInz6obpgDQGcFmaJgB", "voice_name": "Adam"}          # en m

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
        # Single host by default — the user found 2-voice episodes didn't sound
        # like one room. Multi-voice stays fully supported via the hosts list.
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


def seed_categories(db: Session) -> None:
    existing = {slug for (slug,) in db.query(Category.slug).all()}
    for data in SEED_CATEGORIES:
        if data["slug"] not in existing:
            db.add(Category(**data))
    if not db.get(AppSetting, 1):
        db.add(AppSetting(id=1, **{f"default_{k}": v for k, v in VOICE_SANTI.items()}))
    db.commit()
