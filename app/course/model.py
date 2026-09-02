from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    # Course → Chapters
    chapters = relationship(
        "Chapter",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    # Course → Materials
    materials = relationship(
        "Material",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    # Course → One AI Tutor
    tutor = relationship(
        "CourseTutor",
        back_populates="course",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    # Chapter → Course
    course = relationship(
        "Course",
        back_populates="chapters"
    )


class Material(Base):
    __tablename__ = "materials"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String,
        nullable=False
    )

    file_type = Column(
        String,
        nullable=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    # Material → Course
    course = relationship(
        "Course",
        back_populates="materials"
    )


class CourseTutor(Base):
    __tablename__ = "course_tutors"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False,
        unique=True
    )

    # -----------------------------------------------------
    # AI TUTOR CONFIGURATION
    # -----------------------------------------------------

    tutor_name = Column(
        String,
        nullable=False,
        default="Lyra"
    )

    personality = Column(
        String,
        nullable=False,
        default="friendly"
    )

    teaching_style = Column(
        String,
        nullable=False,
        default="step-by-step"
    )

    tone = Column(
        String,
        nullable=False,
        default="encouraging"
    )

    difficulty = Column(
        String,
        nullable=False,
        default="beginner-friendly"
    )

    custom_instructions = Column(
        Text,
        nullable=True
    )

    # CourseTutor → Course
    course = relationship(
        "Course",
        back_populates="tutor"
    )