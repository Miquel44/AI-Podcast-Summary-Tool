from sqlalchemy.orm import Session

from .models import AppSetting, Show, ShowKind

# ElevenLabs premade multilingual voices (work well in Spanish).
VOICE_RACHEL = {"voice_id": "21m00Tcm4TlvDq8ikWAM", "voice_name": "Rachel"}
VOICE_ADAM = {"voice_id": "pNInz6obpgDQGcFmaJgB", "voice_name": "Adam"}

SEED_SHOWS = [
    dict(
        slug="ia-al-dia",
        title="IA al Día",
        tagline="Lanzamientos de modelos y cómo funcionan por dentro",
        interest_prompt=(
            "Noticias de inteligencia artificial: lanzamientos de modelos (p. ej. GLM 5.3 "
            "Flash, nuevas herramientas como Gemini Text-to-Speech), novedades de Anthropic, "
            "OpenAI, Google DeepMind y laboratorios chinos. Me interesa especialmente el "
            "detalle técnico de cómo funcionan los modelos, no solo el anuncio."
        ),
        category="tech",
        kind=ShowKind.news,
        cover_from="#4c1d95",
        cover_to="#2563eb",
        cover_icon="🤖",
        hosts=[
            {**VOICE_RACHEL, "persona": "presentadora curiosa que hace las preguntas"},
            {**VOICE_ADAM, "persona": "experto técnico que explica cómo funcionan los modelos"},
        ],
    ),
    dict(
        slug="mercados-hoy",
        title="Mercados Hoy",
        tagline="Bolsa y noticias financieras del día",
        interest_prompt=(
            "Noticias financieras y de bolsa: movimientos de mercado, resultados de grandes "
            "tecnológicas, macroeconomía (Fed, BCE), y contexto de por qué se mueve el mercado."
        ),
        category="finance",
        kind=ShowKind.news,
        cover_from="#064e3b",
        cover_to="#10b981",
        cover_icon="📈",
    ),
    dict(
        slug="politica-eeuu",
        title="Política EE.UU.",
        tagline="La actualidad política estadounidense",
        interest_prompt=(
            "Noticias políticas de Estados Unidos: Casa Blanca, Congreso, elecciones, "
            "política exterior y regulación tecnológica."
        ),
        category="politics",
        kind=ShowKind.news,
        cover_from="#1e3a8a",
        cover_to="#dc2626",
        cover_icon="🇺🇸",
    ),
    dict(
        slug="politica-colombia",
        title="Política Colombia",
        tagline="La actualidad política colombiana",
        interest_prompt=(
            "Noticias políticas de Colombia: gobierno, Congreso, elecciones, economía "
            "política y relaciones internacionales."
        ),
        category="politics",
        kind=ShowKind.news,
        cover_from="#713f12",
        cover_to="#eab308",
        cover_icon="🇨🇴",
    ),
    dict(
        slug="politica-espana",
        title="Política España",
        tagline="La actualidad política española",
        interest_prompt=(
            "Noticias políticas de España: Gobierno, Congreso, comunidades autónomas, "
            "elecciones y relación con la UE."
        ),
        category="politics",
        kind=ShowKind.news,
        cover_from="#7f1d1d",
        cover_to="#f59e0b",
        cover_icon="🇪🇸",
    ),
    dict(
        slug="fun-facts-historia",
        title="Fun Facts de Historia",
        tagline="Curiosidades de Roma, Grecia y más allá",
        interest_prompt=(
            "Curiosidades históricas sorprendentes y poco conocidas: Roma y Grecia "
            "antiguas, historia de España, Segunda Guerra Mundial y siglo XX. Tono ligero "
            "y entretenido."
        ),
        category="history",
        kind=ShowKind.evergreen,
        cover_from="#78350f",
        cover_to="#d97706",
        cover_icon="🏛️",
    ),
    dict(
        slug="historia-en-profundidad",
        title="Historia en Profundidad",
        tagline="Una guerra o una época, contada entera",
        interest_prompt=(
            "Historia resumida en profundidad: un episodio cubre un tema completo, como una "
            "guerra entera o una etapa histórica (p. ej. la Segunda República española, las "
            "Guerras Púnicas, la Guerra Civil). Riguroso pero narrativo."
        ),
        category="history",
        kind=ShowKind.evergreen,
        cover_from="#374151",
        cover_to="#9ca3af",
        cover_icon="⚔️",
    ),
]


def seed_shows(db: Session) -> None:
    existing = {slug for (slug,) in db.query(Show.slug).all()}
    for data in SEED_SHOWS:
        if data["slug"] not in existing:
            db.add(Show(**data))
    if not db.get(AppSetting, 1):
        db.add(AppSetting(id=1, **{f"default_{k}": v for k, v in VOICE_RACHEL.items()}))
    db.commit()
