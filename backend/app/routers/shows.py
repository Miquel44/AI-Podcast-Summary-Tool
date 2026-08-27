from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Show
from ..schemas import EpisodeOut, ShowOut, ShowUpdate

router = APIRouter(prefix="/api/shows", tags=["shows"])


@router.get("", response_model=list[ShowOut])
def list_shows(db: Session = Depends(get_db)):
    return db.query(Show).order_by(Show.id).all()


@router.get("/{show_id}", response_model=ShowOut)
def get_show(show_id: int, db: Session = Depends(get_db)):
    show = db.get(Show, show_id)
    if not show:
        raise HTTPException(404, "Show not found")
    return show


@router.patch("/{show_id}", response_model=ShowOut)
def update_show(show_id: int, payload: ShowUpdate, db: Session = Depends(get_db)):
    show = db.get(Show, show_id)
    if not show:
        raise HTTPException(404, "Show not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(show, field, value)
    db.commit()
    return show


@router.get("/{show_id}/episodes", response_model=list[EpisodeOut])
def list_episodes(show_id: int, db: Session = Depends(get_db)):
    show = db.get(Show, show_id)
    if not show:
        raise HTTPException(404, "Show not found")
    return show.episodes
