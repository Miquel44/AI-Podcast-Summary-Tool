import io
import logging
from pathlib import Path

import httpx
from pydub import AudioSegment

from ..config import TTS_PRICE_PER_1K_CHARS, settings
from .llm import record_usage

log = logging.getLogger(__name__)

# Each API call renders the voice with slightly different acoustic character
# ("different take" artifact). Defenses, applied together:
#   1. few, large blocks (fewer boundaries),
#   2. previous_text/next_text so prosody flows across those boundaries,
#   3. loudness matching between segments.
# Request-id stitching (conditioning on the previous AUDIO) would be stronger,
# but this account runs in high privacy mode and the API rejects it — hence
# the REST call is kept minimal and text-context only.
MAX_BLOCK_CHARS = 4500

_API = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

VOICE_SETTINGS = {
    "stability": 0.62,
    "similarity_boost": 0.8,
    "style": 0.15,
    "use_speaker_boost": True,
}


def _blocks(lines: list[dict]) -> list[dict]:
    """Merge consecutive same-host lines into large blocks."""
    blocks: list[dict] = []
    for line in lines:
        current = blocks[-1] if blocks else None
        if (
            current
            and current["host"] == line["host"]
            and len(current["text"]) + len(line["text"]) < MAX_BLOCK_CHARS
        ):
            current["text"] += "\n\n" + line["text"]
        else:
            blocks.append({"host": line["host"], "text": line["text"]})
    return blocks


def _convert(voice_id: str, text: str, prev_text: str | None, next_text: str | None) -> bytes:
    """One TTS request with text-context stitching."""
    body: dict = {
        "text": text,
        "model_id": settings.elevenlabs_model,
        "voice_settings": VOICE_SETTINGS,
    }
    if prev_text:
        body["previous_text"] = prev_text[-500:]
    if next_text:
        body["next_text"] = next_text[:500]
    resp = httpx.post(
        _API.format(voice_id=voice_id),
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": settings.elevenlabs_api_key},
        json=body,
        timeout=300,
    )
    resp.raise_for_status()
    return resp.content


def synthesize_episode(lines: list[dict], hosts: list[dict], out_path: Path) -> float:
    """TTS in per-speaker blocks stitched by request id. Returns duration (s)."""
    blocks = _blocks(lines)
    gap = AudioSegment.silent(duration=280)
    audio = AudioSegment.silent(duration=150)
    target_dbfs: float | None = None

    for i, block in enumerate(blocks):
        voice_id = hosts[block["host"]]["voice_id"]
        prev_text = next(
            (b["text"] for b in reversed(blocks[:i]) if b["host"] == block["host"]), None
        )
        next_text = next(
            (b["text"] for b in blocks[i + 1 :] if b["host"] == block["host"]), None
        )
        raw = _convert(voice_id, block["text"], prev_text, next_text)

        segment = AudioSegment.from_file(io.BytesIO(raw), format="mp3")
        if segment.dBFS != float("-inf"):
            if target_dbfs is None:
                target_dbfs = segment.dBFS
            else:
                segment = segment.apply_gain(target_dbfs - segment.dBFS)
        audio = audio + segment + gap
        log.info("tts block %d/%d done (%.1fs)", i + 1, len(blocks), len(segment) / 1000)

    audio.export(out_path, format="mp3", bitrate="128k")
    chars = sum(len(l["text"]) for l in lines)
    record_usage(
        "tts", settings.elevenlabs_model, meta=out_path.stem,
        characters=chars, cost_usd=chars / 1000 * TTS_PRICE_PER_1K_CHARS,
    )
    return len(audio) / 1000.0
