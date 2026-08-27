import logging
import threading

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AppSetting, Category
from ..schemas import AppSettingsOut, AppSettingsUpdate
from ..seed import CATEGORY_TITLES

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _get_or_create(db: Session) -> AppSetting:
    row = db.get(AppSetting, 1)
    if not row:
        row = AppSetting(id=1)
        db.add(row)
        db.commit()
    return row


@router.get("", response_model=AppSettingsOut)
def get_settings(db: Session = Depends(get_db)):
    return _get_or_create(db)


@router.patch("", response_model=AppSettingsOut)
def update_settings(payload: AppSettingsUpdate, db: Session = Depends(get_db)):
    row = _get_or_create(db)
    changes = payload.model_dump(exclude_unset=True)
    language_changed = "language" in changes and changes["language"] != row.language
    for field, value in changes.items():
        setattr(row, field, value)
    db.commit()

    if language_changed:
        # Editions are cached per language: nothing is deleted. Categories are
        # retitled, and any category with no fresh edition in the new language
        # materializes lazily in the background (first visit only).
        log.info("language changed to %s: activating that edition", row.language)
        for cat in db.query(Category).all():
            titles = CATEGORY_TITLES.get(cat.slug)
            if titles and row.language in titles:
                cat.title = titles[row.language]
        db.commit()
        from .. import scheduler

        threading.Thread(target=scheduler.refresh_all, daemon=True).start()
    return row
