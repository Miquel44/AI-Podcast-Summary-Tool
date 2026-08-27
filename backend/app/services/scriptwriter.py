from ..config import settings
from ..models import Category, Story
from . import llm
from .discovery import LANGUAGES

# Style guide: sober, confident, human. The user's feedback: earlier drafts
# tried too hard to be funny and felt forced — humor must never be sought.
_STYLE = """ESTILO (muy importante):
- Lenguaje natural HABLADO, sobrio y con confianza: como un periodista de podcast
  que domina el tema y respeta al oyente, no un animador.
- EL HUMOR NO SE BUSCA. Nada de chistes, símiles estrafalarios, exageraciones
  ("invade media Internet"), ni ocurrencias. Como mucho, una ironía seca y breve
  si surge sola del material. Si dudas, elimínala.
- Curiosidad genuina y claridad: cifras, nombres, causas y consecuencias.
  Explica lo técnico con calma y precisión, sin infantilizar ni dramatizar.
- Frases de longitud variada, transiciones orgánicas, ritmo tranquilo.
- PROHIBIDO el registro robótico de IA: nada de "en resumen", "cabe destacar",
  "es importante mencionar", "sin duda", listas enumeradas leídas, ni cierres genéricos.
- No leas titulares: cuenta la historia con sus hechos, contexto y por qué importa.
- Todo debe poder pronunciarse: sin siglas crípticas sin explicar, sin URLs, sin markdown."""

_MONO_SYSTEM = f"""Eres el guionista de un podcast personal con un único presentador.
Escribe el guion completo del episodio sobre la historia que se te da.

{_STYLE}

Estructura: gancho inicial (frío, directo a lo interesante), desarrollo con los hechos y
su contexto, y un cierre con una idea que se quede en la cabeza. Sin sintonías ni
"bienvenidos a otro episodio": entra directo.

Devuelve JSON: {{"title": "título del episodio", "lines": [{{"host": 0, "text": "..."}}]}}
Divide el guion en párrafos cortos (2-4 frases por línea)."""

_DIALOGUE_SYSTEM = f"""Eres el guionista de un podcast personal con VARIOS presentadores
que conversan entre ellos. Escribe el episodio como un diálogo vivo y natural.

{_STYLE}

Reglas del diálogo:
- Cada presentador mantiene su personalidad (se te dan las personas).
- Conversación adulta y serena: preguntas de verdad, matices, algún desacuerdo suave.
  Las reacciones son sobrias ("ya", "claro", "eso no lo sabía"), nunca aspavientos.
- Nada de turnos simétricos perfectos: que fluya como una conversación real.
- Entra directo a la conversación, sin presentaciones formales.

Devuelve JSON: {{"title": "título del episodio", "lines": [{{"host": índice_del_presentador, "text": "..."}}]}}
Cada línea es una intervención de un presentador (1-4 frases)."""


def write_script(
    story: Story,
    category: Category,
    hosts: list[dict],
    model: str | None = None,
    language: str = "en",
) -> dict:
    """Returns {"title": ..., "lines": [{"host": int, "text": str}, ...]}.

    `model` forces a specific OpenAI model (used by the bake-off); otherwise the
    configured script provider/model decides.
    """
    sources_txt = "\n".join(
        f"- [{a['source']}] {a['title']}" for a in (story.source_articles or [])
    ) or "(sin artículos: tema evergreen, usa tu conocimiento con rigor)"

    if len(hosts) >= 2:
        system = _DIALOGUE_SYSTEM
        cast = "\n".join(
            f"- Presentador {i} ({h['voice_name']}): {h.get('persona') or 'presentador'}"
            for i, h in enumerate(hosts)
        )
    else:
        system = _MONO_SYSTEM
        cast = f"- Presentador 0 ({hosts[0]['voice_name']})"

    user = (
        f"HISTORIA: {story.title}\n"
        f"CONTEXTO: {story.tagline}\n"
        f"RESUMEN: {story.summary}\n\n"
        f"ARTÍCULOS DE RESPALDO:\n{sources_txt}\n\n"
        f"INTERESES DEL OYENTE (ajusta el enfoque):\n{category.interest_prompt}\n\n"
        f"REPARTO:\n{cast}\n\n"
        f"IDIOMA DEL GUION: escribe título y TODO el guion en "
        f"{LANGUAGES.get(language, LANGUAGES['en'])}.\n"
        f"LONGITUD MÁXIMA (estricta): {settings.episode_target_words} palabras en total. "
        f"No la superes: mejor profundizar en menos puntos que cubrirlo todo."
    )
    data = llm.chat_json(system, user, model=model) if model else llm.script_json(system, user)

    lines = [
        {"host": int(l.get("host", 0)), "text": str(l.get("text", "")).strip()}
        for l in data.get("lines", [])
        if str(l.get("text", "")).strip()
    ]
    # Clamp host indices to the cast size.
    for l in lines:
        if not 0 <= l["host"] < len(hosts):
            l["host"] = 0
    return {"title": data.get("title", story.title), "lines": lines}
