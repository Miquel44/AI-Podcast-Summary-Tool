import json
import logging

from openai import OpenAI

from ..config import settings

log = logging.getLogger(__name__)

_client: OpenAI | None = None


def client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def chat_json(system: str, user: str, model: str | None = None) -> dict:
    """One JSON-mode chat call. The prompts must describe the exact shape."""
    resp = client().chat.completions.create(
        model=model or settings.openai_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
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


def script_json(system: str, user: str) -> dict:
    """JSON call routed to the configured scriptwriting provider/model."""
    if settings.script_provider == "gemini" and settings.gemini_api_key:
        return gemini_json(system, user)
    return chat_json(system, user, model=settings.script_model)
