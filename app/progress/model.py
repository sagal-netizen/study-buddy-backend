from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.base import Base


class ChapterProgress(Base):
    __tablename__ = "chapter_progress"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    chapter_id = Column(
        Integer,
        ForeignKey("chapters.id"),
        nullable=False
    )

    completed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    user = relationship(
        "User"
    )

    chapter = relationship(
        "Chapter"
    )