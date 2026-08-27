import logging
import traceback

from ..config import settings
from ..database import SessionLocal
from ..models import AppSetting, Episode, Story, StoryStatus
from . import scriptwriter, tts
from .discovery import content_language

log = logging.getLogger(__name__)


def resolve_hosts(db, category) -> list[dict]:
    """Category hosts, or a single host with the app default voice."""
    if category.hosts:
        return category.hosts
    setting = db.get(AppSetting, 1)
    if setting and setting.default_voice_id:
        return [{
            "voice_id": setting.default_voice_id,
            "voice_name": setting.default_voice_name or "Narrador",
            "persona": "presentador",
        }]
    # Last-resort fallback: ElevenLabs premade "Rachel".
    return [{"voice_id": "21m00Tcm4TlvDq8ikWAM", "voice_name": "Rachel", "persona": "presentadora"}]


def generate_episode(story_id: int) -> None:
    """Full pipeline for one story: script (OpenAI) -> TTS (ElevenLabs) -> mp3.

    Runs in a background task with its own DB session.
    """
    db = SessionLocal()
    try:
        story = db.get(Story, story_id)
        if not story:
            return
        story.status = StoryStatus.generating
        db.commit()

        hosts = resolve_hosts(db, story.category)
        language = content_language(db)
        script = scriptwriter.write_script(story, story.category, hosts, language=language)
        episode = Episode(story_id=story.id, title=script["title"], script=script["lines"])
        db.add(episode)
        db.commit()

        out_path = settings.storage_dir / "episodes" / f"episode_{episode.id}.mp3"
        duration = tts.synthesize_episode(script["lines"], hosts, out_path)

        episode.audio_path = f"/storage/episodes/{out_path.name}"
        episode.duration_s = duration
        story.status = StoryStatus.ready
        db.commit()
        log.info("episode %d ready (%.0fs)", episode.id, duration)
    except Exception as exc:
        log.error("generation failed for story %d: %s\n%s", story_id, exc, traceback.format_exc())
        db.rollback()
        story = db.get(Story, story_id)
        if story:
            story.status = StoryStatus.failed
            for ep in story.episodes:
                if ep.audio_path is None and ep.error is None:
                    ep.error = str(exc)
            db.commit()
    finally:
        db.close()
