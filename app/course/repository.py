from sqlalchemy.orm import Session

from .model import Course, Chapter, Material


# =========================================================
# COURSE
# =========================================================

def create_course(
    db: Session,
    title: str,
    description: str | None = None
):
    new_course = Course(
        title=title,
        description=description
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


def get_courses(db: Session):
    return (
        db.query(Course)
        .order_by(Course.id)
        .all()
    )


def get_course_by_id(
    db: Session,
    course_id: int
):
    return (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )


def update_course(
    db: Session,
    course_id: int,
    title: str,
    description: str | None = None
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        return None

    course.title = title
    course.description = description

    db.commit()
    db.refresh(course)

    return course


def delete_course(
    db: Session,
    course_id: int
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        return None

    db.delete(course)
    db.commit()

    return course


# =========================================================
# CHAPTER
# =========================================================

def create_chapter(
    db: Session,
    course_id: int,
    title: str,
    content: str | None = None,
    notes: str | None = None
):
    new_chapter = Chapter(
        course_id=course_id,
        title=title,
        content=content,
        notes=notes
    )

    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)

    return new_chapter


def get_chapters(
    db: Session,
    course_id: int
):
    return (
        db.query(Chapter)
        .filter(
            Chapter.course_id == course_id
        )
        .order_by(Chapter.id)
        .all()
    )


def get_chapter_by_id(
    db: Session,
    chapter_id: int
):
    return (
        db.query(Chapter)
        .filter(Chapter.id == chapter_id)
        .first()
    )


def update_chapter(
    db: Session,
    chapter_id: int,
    title: str,
    content: str | None = None,
    notes: str | None = None
):
    chapter = get_chapter_by_id(
        db,
        chapter_id
    )

    if not chapter:
        return None

    chapter.title = title
    chapter.content = content
    chapter.notes = notes

    db.commit()
    db.refresh(chapter)

    return chapter


def delete_chapter(
    db: Session,
    chapter_id: int
):
    chapter = get_chapter_by_id(
        db,
        chapter_id
    )

    if not chapter:
        return None

    db.delete(chapter)
    db.commit()

    return chapter


# =========================================================
# MATERIAL
# =========================================================

def create_material(
    db: Session,
    course_id: int,
    filename: str,
    file_path: str,
    file_type: str | None = None,
    chapter_id: int | None = None
):
    new_material = Material(
        course_id=course_id,
        chapter_id=chapter_id,
        filename=filename,
        file_path=file_path,
        file_type=file_type
    )

    db.add(new_material)
    db.commit()
    db.refresh(new_material)

    return new_material


def get_materials(
    db: Session,
    course_id: int
):
    return (
        db.query(Material)
        .filter(
            Material.course_id == course_id
        )
        .order_by(Material.id)
        .all()
    )


def get_material_by_id(
    db: Session,
    material_id: int
):
    return (
        db.query(Material)
        .filter(
            Material.id == material_id
        )
        .first()
    )


def delete_material(
    db: Session,
    material_id: int
):
    material = get_material_by_id(
        db,
        material_id
    )

    if not material:
        return None

    db.delete(material)
    db.commit()

    return material