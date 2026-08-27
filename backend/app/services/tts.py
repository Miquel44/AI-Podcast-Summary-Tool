import io
import logging
from pathlib import Path

from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

from ..config import TTS_PRICE_PER_1K_CHARS, settings
from .llm import record_usage

log = logging.getLogger(__name__)

_client: ElevenLabs | None = None


def client() -> ElevenLabs:
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    return _client


def synthesize_episode(lines: list[dict], hosts: list[dict], out_path: Path) -> float:
    """TTS each line with its host's voice, stitch with short gaps. Returns duration (s)."""
    gap = AudioSegment.silent(duration=280)
    audio = AudioSegment.silent(duration=150)

    for i, line in enumerate(lines):
        voice_id = hosts[line["host"]]["voice_id"]
        chunks = client().text_to_speech.convert(
            voice_id=voice_id,
            text=line["text"],
            model_id=settings.elevenlabs_model,
            output_format="mp3_44100_128",
        )
        raw = b"".join(chunks)
        segment = AudioSegment.from_file(io.BytesIO(raw), format="mp3")
        audio = audio + segment + gap
        log.info("tts line %d/%d done (%.1fs)", i + 1, len(lines), len(segment) / 1000)

    audio.export(out_path, format="mp3", bitrate="128k")
    chars = sum(len(l["text"]) for l in lines)
    record_usage(
        "tts", settings.elevenlabs_model, meta=out_path.stem,
        characters=chars, cost_usd=chars / 1000 * TTS_PRICE_PER_1K_CHARS,
    )
    return len(audio) / 1000.0
