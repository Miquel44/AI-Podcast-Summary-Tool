from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, Story
from ..schemas import StoryOut

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("", response_model=list[StoryOut])
def demo_stories(db: Session = Depends(get_db)):
    """Pre-generated showcase episodes (seeded from the committed demo/ folder).

    Served regardless of the active UI language — they exist so a reviewer can
    hit play in second one, before the daily edition finishes populating.
    """
    category = db.query(Category).filter(Category.slug == "demo").first()
    if not category:
        return []
    return (
        db.query(Story).filter(Story.category_id == category.id).order_by(Story.id).all()
    )
