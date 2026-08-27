from sqlalchemy.orm import Session

from .models import AppSetting, Category, CategoryKind

# ElevenLabs premade multilingual voices (work well in Spanish).
VOICE_RACHEL = {"voice_id": "21m00Tcm4TlvDq8ikWAM", "voice_name": "Rachel"}
VOICE_ADAM = {"voice_id": "pNInz6obpgDQGcFmaJgB", "voice_name": "Adam"}

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
        hosts=[
            {**VOICE_RACHEL, "persona": "presentadora curiosa que hace las preguntas"},
            {**VOICE_ADAM, "persona": "experto técnico que explica cómo funcionan los modelos"},
        ],
    ),
    dict(
        slug="finance",
        title="Finanzas",
        position=1,
        interest_prompt=(
            "Noticias financieras y de bolsa: movimientos de mercado, resultados de grandes "
            "tecnológicas, macroeconomía (Fed, BCE), y contexto de por qué se mueve el mercado."
        ),
        kind=CategoryKind.news,
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
    ),
]


def seed_categories(db: Session) -> None:
    existing = {slug for (slug,) in db.query(Category.slug).all()}
    for data in SEED_CATEGORIES:
        if data["slug"] not in existing:
            db.add(Category(**data))
    if not db.get(AppSetting, 1):
        db.add(AppSetting(id=1, **{f"default_{k}": v for k, v in VOICE_RACHEL.items()}))
    db.commit()
