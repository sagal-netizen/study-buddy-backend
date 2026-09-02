from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.security import get_current_user

from .repository import (
    mark_chapter_complete,
    get_user_progress,
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# MARK CHAPTER COMPLETE
# A student can only mark progress for their own account.
# =========================

@router.post(
    "/progress/{user_id}/{chapter_id}/complete"
)
def complete_chapter(
    user_id: int,
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Enforce that the authenticated user matches
    # the user_id in the URL.  Admins may bypass this.
    if (
        current_user.get("user_id") != user_id
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own progress"
        )

    progress = mark_chapter_complete(
        db,
        user_id,
        chapter_id
    )

    return {
        "message": "Chapter marked as completed",
        "progress": {
            "id": progress.id,
            "user_id": progress.user_id,
            "chapter_id": progress.chapter_id,
            "completed": progress.completed
        }
    }


# =========================
# GET USER PROGRESS
# A student can only read their own progress.
# =========================

@router.get(
    "/progress/{user_id}"
)
def user_progress(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if (
        current_user.get("user_id") != user_id
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only view your own progress"
        )

    progress = get_user_progress(
        db,
        user_id
    )

    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "chapter_id": item.chapter_id,
            "completed": item.completed
        }
        for item in progress
    ]
