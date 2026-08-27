import json
import logging

from openai import OpenAI

from ..config import MODEL_PRICES, settings

log = logging.getLogger(__name__)

_client: OpenAI | None = None


def client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def record_usage(
    kind: str,
    model: str,
    meta: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
    characters: int = 0,
    cost_usd: float | None = None,
) -> None:
    """Append one row to the real-cost ledger. Never breaks the caller."""
    try:
        from ..database import SessionLocal
        from ..models import UsageLog

        if cost_usd is None:
            price_in, price_out = MODEL_PRICES.get(model, (0.0, 0.0))
            cost_usd = (input_tokens * price_in + output_tokens * price_out) / 1_000_000
        with SessionLocal() as db:
            db.add(UsageLog(
                kind=kind, model=model, meta=meta,
                input_tokens=input_tokens, output_tokens=output_tokens,
                characters=characters, cost_usd=round(cost_usd, 6),
            ))
            db.commit()
    except Exception as exc:
        log.warning("usage log failed: %s", exc)


def chat_json(
    system: str, user: str, model: str | None = None, kind: str = "llm", meta: str = ""
) -> dict:
    """One JSON-mode chat call. The prompts must describe the exact shape."""
    model = model or settings.openai_model
    resp = client().chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    usage = resp.usage
    record_usage(
        kind, model, meta,
        input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
        output_tokens=getattr(usage, "completion_tokens", 0) or 0,
    )
    return json.loads(resp.choices[0].message.content)


def gemini_json(system: str, user: str, model: str | None = None) -> dict:
    """Same contract as chat_json, via the Gemini API (google-genai SDK)."""
    from google import genai
    from google.genai import types

    gclient = genai.Client(api_key=settings.gemini_api_key)
    resp = gclient.models.generate_content(
        model=model or settings.gemini_model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
        ),
    )
    return json.loads(resp.text)


def script_json(system: str, user: str, meta: str = "") -> dict:
    """JSON call routed to the configured scriptwriting provider/model."""
    if settings.script_provider == "gemini" and settings.gemini_api_key:
        return gemini_json(system, user)
    return chat_json(system, user, model=settings.script_model, kind="script", meta=meta)
