"""Daily-edition scheduler.

Like a real product: every user opens the app to an already-populated home.
On startup (and daily at 06:00) each category discovers its stories in the
background; the UI simply polls and the rows fill in.
"""

import logging
import threading
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .database import SessionLocal
from .models import Category, Story, StoryStatus
from .services import discovery

log = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None
FRESH_HOURS = 20  # a category with stories newer than this skips the refresh


def _is_fresh(db, category: Category) -> bool:
    latest = (
        db.query(Story)
        .filter(Story.category_id == category.id)
        .order_by(Story.id.desc())
        .first()
    )
    return bool(latest and datetime.utcnow() - latest.created_at < timedelta(hours=FRESH_HOURS))


def refresh_all(force: bool = False) -> None:
    db = SessionLocal()
    try:
        for category in db.query(Category).filter(Category.enabled.is_(True)).all():
            if not force and _is_fresh(db, category):
                continue
            try:
                created = discovery.discover(db, category)
                log.info("daily edition: %s -> %d stories", category.slug, len(created))
            except Exception as exc:
                log.warning("daily edition failed for %s: %s", category.slug, exc)

        # Prune stale cards nobody turned into an episode.
        cutoff = datetime.utcnow() - timedelta(hours=48)
        db.query(Story).filter(
            Story.status == StoryStatus.suggested, Story.created_at < cutoff
        ).delete()
        db.commit()
    finally:
        db.close()


def start() -> None:
    global _scheduler
    if _scheduler:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(refresh_all, CronTrigger(hour=6, minute=0), id="daily-edition")
    _scheduler.start()
    # Fill the home right away without blocking startup.
    threading.Thread(target=refresh_all, daemon=True).start()
