from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, Story
from ..schemas import CategoryOut, CategoryUpdate, StoryOut
from ..services import discovery

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.position, Category.id).all()


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    return category


@router.get("/{category_id}/stories", response_model=list[StoryOut])
def list_stories(category_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Story)
        .filter(
            Story.category_id == category_id,
            Story.language == discovery.content_language(db),
        )
        .order_by(Story.id.desc())
        .limit(30)
        .all()
    )


@router.post("/{category_id}/discover", response_model=list[StoryOut])
def discover_stories(category_id: int, db: Session = Depends(get_db)):
    """Fetch fresh news and mint new story cards for this row."""
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")
    try:
        return discovery.discover(db, category)
    except Exception as exc:
        raise HTTPException(502, f"Discovery falló: {exc}")
