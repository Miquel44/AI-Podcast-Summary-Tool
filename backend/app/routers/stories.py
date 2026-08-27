from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Story, StoryStatus
from ..schemas import StoryDetail
from ..services import pipeline

router = APIRouter(prefix="/api/stories", tags=["stories"])


@router.get("/{story_id}", response_model=StoryDetail)
def get_story(story_id: int, db: Session = Depends(get_db)):
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(404, "Story not found")
    return story


@router.post("/{story_id}/generate", response_model=StoryDetail)
def generate(story_id: int, background: BackgroundTasks, db: Session = Depends(get_db)):
    """Kick off script + TTS generation for this story in the background."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(404, "Story not found")
    if story.status == StoryStatus.generating:
        return story
    story.status = StoryStatus.generating
    db.commit()
    background.add_task(pipeline.generate_episode, story_id)
    return story
