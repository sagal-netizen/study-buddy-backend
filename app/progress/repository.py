from sqlalchemy.orm import Session

from .model import ChapterProgress


def get_progress(
    db: Session,
    user_id: int,
    chapter_id: int
):
    return db.query(
        ChapterProgress
    ).filter(
        ChapterProgress.user_id == user_id,
        ChapterProgress.chapter_id == chapter_id
    ).first()


def mark_chapter_complete(
    db: Session,
    user_id: int,
    chapter_id: int
):
    progress = get_progress(
        db,
        user_id,
        chapter_id
    )

    if progress:
        progress.completed = True
    else:
        progress = ChapterProgress(
            user_id=user_id,
            chapter_id=chapter_id,
            completed=True
        )

        db.add(progress)

    db.commit()
    db.refresh(progress)

    return progress


def get_user_progress(
    db: Session,
    user_id: int
):
    return db.query(
        ChapterProgress
    ).filter(
        ChapterProgress.user_id == user_id
    ).all()