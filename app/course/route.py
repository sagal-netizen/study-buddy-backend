import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal, UPLOAD_DIRECTORY
from app.security import get_current_user, get_current_admin
from app.ai.document_processor import process_document

from .model import CourseTutor

from .repository import (
    create_course,
    get_courses,
    get_course_by_id,
    update_course,
    delete_course,
    create_chapter,
    get_chapters,
    get_chapter_by_id,
    update_chapter,
    delete_chapter,
    create_material,
    get_materials,
    get_material_by_id,
    delete_material,
)


router = APIRouter()


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# FILE STORAGE
# =========================================================

# Use UPLOAD_DIRECTORY env var if set, otherwise fall back
# to a sibling "uploads/" directory relative to backend root.
if UPLOAD_DIRECTORY:
    UPLOAD_DIR = Path(UPLOAD_DIRECTORY)
else:
    BASE_DIR = Path(__file__).resolve().parents[2]
    UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".txt",
    ".csv",
    ".zip",
}


# =========================================================
# COURSE SCHEMA
# =========================================================

class CourseCreate(BaseModel):
    title: str
    description: str | None = None


# =========================================================
# CHAPTER SCHEMA
# =========================================================

class ChapterCreate(BaseModel):
    title: str
    content: str | None = None
    notes: str | None = None


# =========================================================
# AI TUTOR SCHEMA
# =========================================================

class TutorCreate(BaseModel):
    tutor_name: str = "Lyra"
    personality: str = "friendly"
    teaching_style: str = "step-by-step"
    tone: str = "encouraging"
    difficulty: str = "beginner-friendly"
    custom_instructions: str | None = None


# =========================================================
# COURSE APIs
# =========================================================

@router.post("/courses")
def add_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    new_course = create_course(
        db,
        course.title,
        course.description
    )

    # Create a default AI tutor for the new course
    tutor = CourseTutor(
        course_id=new_course.id,
        tutor_name="Lyra",
        personality="friendly",
        teaching_style="step-by-step",
        tone="encouraging",
        difficulty="beginner-friendly",
        custom_instructions=(
            "Be a helpful academic tutor. "
            "Explain concepts clearly using examples "
            "and encourage the student."
        )
    )

    db.add(tutor)
    db.commit()
    db.refresh(new_course)

    return {
        "message": "Course created successfully",
        "course": {
            "id": new_course.id,
            "title": new_course.title,
            "description": new_course.description
        }
    }


@router.get("/courses")
def get_all_courses(
    db: Session = Depends(get_db)
):
    return get_courses(db)


@router.get("/courses/{course_id}")
def get_single_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


@router.put("/courses/{course_id}")
def edit_course(
    course_id: int,
    course: CourseCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    updated_course = update_course(
        db,
        course_id,
        course.title,
        course.description
    )

    if not updated_course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course updated successfully",
        "course": updated_course
    }


@router.delete("/courses/{course_id}")
def remove_course(
    course_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    deleted_course = delete_course(
        db,
        course_id
    )

    if not deleted_course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course deleted successfully"
    }


# =========================================================
# COURSE-SPECIFIC AI TUTOR
# =========================================================

@router.get("/courses/{course_id}/tutor")
def get_course_tutor(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    tutor = (
        db.query(CourseTutor)
        .filter(
            CourseTutor.course_id == course_id
        )
        .first()
    )

    # Existing courses may not have a tutor yet.
    # Create one automatically.
    if not tutor:

        tutor = CourseTutor(
            course_id=course_id,
            tutor_name="Lyra",
            personality="friendly",
            teaching_style="step-by-step",
            tone="encouraging",
            difficulty="beginner-friendly",
            custom_instructions=(
                "Be a helpful academic tutor. "
                "Explain concepts clearly using examples "
                "and encourage the student."
            )
        )

        db.add(tutor)
        db.commit()
        db.refresh(tutor)

    return {
        "id": tutor.id,
        "course_id": tutor.course_id,
        "tutor_name": tutor.tutor_name,
        "personality": tutor.personality,
        "teaching_style": tutor.teaching_style,
        "tone": tutor.tone,
        "difficulty": tutor.difficulty,
        "custom_instructions": tutor.custom_instructions
    }


@router.post("/courses/{course_id}/tutor")
def create_or_update_course_tutor(
    course_id: int,
    tutor_data: TutorCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    tutor = (
        db.query(CourseTutor)
        .filter(
            CourseTutor.course_id == course_id
        )
        .first()
    )

    if tutor:

        tutor.tutor_name = tutor_data.tutor_name
        tutor.personality = tutor_data.personality
        tutor.teaching_style = tutor_data.teaching_style
        tutor.tone = tutor_data.tone
        tutor.difficulty = tutor_data.difficulty
        tutor.custom_instructions = (
            tutor_data.custom_instructions
        )

    else:

        tutor = CourseTutor(
            course_id=course_id,
            tutor_name=tutor_data.tutor_name,
            personality=tutor_data.personality,
            teaching_style=tutor_data.teaching_style,
            tone=tutor_data.tone,
            difficulty=tutor_data.difficulty,
            custom_instructions=(
                tutor_data.custom_instructions
            )
        )

        db.add(tutor)

    db.commit()
    db.refresh(tutor)

    return {
        "message": "Course AI Tutor saved successfully",
        "tutor": {
            "id": tutor.id,
            "course_id": tutor.course_id,
            "tutor_name": tutor.tutor_name,
            "personality": tutor.personality,
            "teaching_style": tutor.teaching_style,
            "tone": tutor.tone,
            "difficulty": tutor.difficulty,
            "custom_instructions": tutor.custom_instructions
        }
    }


@router.put("/courses/{course_id}/tutor")
def update_course_tutor(
    course_id: int,
    tutor_data: TutorCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    tutor = (
        db.query(CourseTutor)
        .filter(
            CourseTutor.course_id == course_id
        )
        .first()
    )

    if not tutor:

        tutor = CourseTutor(
            course_id=course_id
        )

        db.add(tutor)

    tutor.tutor_name = tutor_data.tutor_name
    tutor.personality = tutor_data.personality
    tutor.teaching_style = tutor_data.teaching_style
    tutor.tone = tutor_data.tone
    tutor.difficulty = tutor_data.difficulty
    tutor.custom_instructions = (
        tutor_data.custom_instructions
    )

    db.commit()
    db.refresh(tutor)

    return {
        "message": "Course AI Tutor updated successfully",
        "tutor": {
            "id": tutor.id,
            "course_id": tutor.course_id,
            "tutor_name": tutor.tutor_name,
            "personality": tutor.personality,
            "teaching_style": tutor.teaching_style,
            "tone": tutor.tone,
            "difficulty": tutor.difficulty,
            "custom_instructions": tutor.custom_instructions
        }
    }


# =========================================================
# CHAPTER APIs
# =========================================================

@router.post("/courses/{course_id}/chapters")
def add_chapter(
    course_id: int,
    chapter: ChapterCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    new_chapter = create_chapter(
        db,
        course_id,
        chapter.title,
        chapter.content,
        chapter.notes
    )

    return {
        "message": "Chapter created successfully",
        "chapter": {
            "id": new_chapter.id,
            "title": new_chapter.title,
            "content": new_chapter.content,
            "notes": new_chapter.notes,
            "course_id": new_chapter.course_id
        }
    }


@router.get("/courses/{course_id}/chapters")
def get_course_chapters(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return get_chapters(
        db,
        course_id
    )


@router.get("/chapters/{chapter_id}")
def get_single_chapter(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    chapter = get_chapter_by_id(
        db,
        chapter_id
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Chapter not found"
        )

    return chapter


@router.put("/chapters/{chapter_id}")
def edit_chapter(
    chapter_id: int,
    chapter: ChapterCreate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    updated_chapter = update_chapter(
        db,
        chapter_id,
        chapter.title,
        chapter.content,
        chapter.notes
    )

    if not updated_chapter:
        raise HTTPException(
            status_code=404,
            detail="Chapter not found"
        )

    return {
        "message": "Chapter updated successfully",
        "chapter": updated_chapter
    }


@router.delete("/chapters/{chapter_id}")
def remove_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    deleted_chapter = delete_chapter(
        db,
        chapter_id
    )

    if not deleted_chapter:
        raise HTTPException(
            status_code=404,
            detail="Chapter not found"
        )

    return {
        "message": "Chapter deleted successfully"
    }


# =========================================================
# HELPER — SAVE UPLOADED FILE
# =========================================================

async def save_uploaded_file(
    file: UploadFile
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    original_filename = Path(
        file.filename
    ).name

    file_extension = Path(
        original_filename
    ).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "File type not allowed. "
                "Allowed types: PDF, DOC, DOCX, "
                "PPT, PPTX, XLS, XLSX, TXT, CSV, ZIP"
            )
        )

    unique_filename = (
        f"{uuid.uuid4().hex}"
        f"{file_extension}"
    )

    file_path = (
        UPLOAD_DIR /
        unique_filename
    )

    try:
        with open(
            file_path,
            "wb"
        ) as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception:

        if file_path.exists():
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail="Could not save uploaded file"
        )

    finally:
        await file.close()

    return (
        original_filename,
        file_extension,
        file_path
    )


# =========================================================
# CHAPTER-SPECIFIC MATERIAL UPLOAD
# =========================================================

@router.post(
    "/courses/{course_id}/chapters/{chapter_id}/materials"
)
async def upload_chapter_material(
    course_id: int,
    chapter_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    chapter = get_chapter_by_id(
        db,
        chapter_id
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Chapter not found"
        )

    if chapter.course_id != course_id:
        raise HTTPException(
            status_code=400,
            detail="Chapter does not belong to this course"
        )

    (
        original_filename,
        file_extension,
        file_path
    ) = await save_uploaded_file(file)

    material = create_material(
        db=db,
        course_id=course_id,
        filename=original_filename,
        file_path=str(file_path),
        file_type=file_extension.lstrip("."),
        chapter_id=chapter_id
    )

    processing_result = {
        "success": False,
        "chunks": 0,
        "message": "Document type not processed."
    }

    supported_ai_types = {
        ".pdf",
        ".docx",
        ".txt"
    }

    if file_extension in supported_ai_types:

        try:

            processing_result = process_document(
                file_path=str(file_path),
                file_type=file_extension.lstrip("."),
                material_id=material.id,
                course_id=course_id,
                chapter_id=chapter_id
            )

            print(
                "AI document processing:",
                processing_result
            )

        except Exception as error:

            print(
                "Document processing failed:",
                error
            )

            processing_result = {
                "success": False,
                "chunks": 0,
                "message": (
                    "File uploaded, but AI processing failed."
                )
            }

    return {
        "message": (
            "Chapter material uploaded successfully"
        ),

        "material": {
            "id": material.id,
            "filename": material.filename,
            "file_type": material.file_type,
            "course_id": material.course_id,
            "chapter_id": material.chapter_id
        },

        "ai_processing": processing_result
    }


# =========================================================
# COURSE-LEVEL MATERIAL UPLOAD
# =========================================================

@router.post(
    "/courses/{course_id}/materials"
)
async def upload_material(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    (
        original_filename,
        file_extension,
        file_path
    ) = await save_uploaded_file(file)

    material = create_material(
        db=db,
        course_id=course_id,
        filename=original_filename,
        file_path=str(file_path),
        file_type=file_extension.lstrip(".")
    )

    processing_result = {
        "success": False,
        "chunks": 0,
        "message": "Document type not processed."
    }

    supported_ai_types = {
        ".pdf",
        ".docx",
        ".txt"
    }

    if file_extension in supported_ai_types:

        try:

            processing_result = process_document(
                file_path=str(file_path),
                file_type=file_extension.lstrip("."),
                material_id=material.id,
                course_id=course_id,
                chapter_id=None
            )

            print(
                "AI document processing:",
                processing_result
            )

        except Exception as error:

            print(
                "Document processing failed:",
                error
            )

    return {
        "message": "Material uploaded successfully",

        "material": {
            "id": material.id,
            "filename": material.filename,
            "file_type": material.file_type,
            "course_id": material.course_id,
            "chapter_id": material.chapter_id
        },

        "ai_processing": processing_result
    }


# =========================================================
# GET COURSE MATERIALS
# =========================================================

@router.get(
    "/courses/{course_id}/materials"
)
def get_course_materials(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    materials = get_materials(
        db,
        course_id
    )

    return [
        {
            "id": material.id,
            "filename": material.filename,
            "file_type": material.file_type,
            "course_id": material.course_id,
            "chapter_id": material.chapter_id
        }
        for material in materials
    ]


# =========================================================
# GET CHAPTER MATERIALS
# =========================================================

@router.get(
    "/courses/{course_id}/chapters/{chapter_id}/materials"
)
def get_chapter_materials(
    course_id: int,
    chapter_id: int,
    db: Session = Depends(get_db)
):
    course = get_course_by_id(
        db,
        course_id
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    chapter = get_chapter_by_id(
        db,
        chapter_id
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Chapter not found"
        )

    if chapter.course_id != course_id:
        raise HTTPException(
            status_code=400,
            detail="Chapter does not belong to this course"
        )

    materials = [
        material
        for material in get_materials(
            db,
            course_id
        )
        if material.chapter_id == chapter_id
    ]

    return [
        {
            "id": material.id,
            "filename": material.filename,
            "file_type": material.file_type,
            "course_id": material.course_id,
            "chapter_id": material.chapter_id
        }
        for material in materials
    ]


# =========================================================
# DOWNLOAD MATERIAL
# =========================================================

@router.get(
    "/materials/{material_id}/download"
)
def download_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    material = get_material_by_id(
        db,
        material_id
    )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    file_path = Path(
        material.file_path
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found on server"
        )

    return FileResponse(
        path=file_path,
        filename=material.filename,
        media_type="application/octet-stream"
    )


# =========================================================
# DELETE MATERIAL
# =========================================================

@router.delete(
    "/materials/{material_id}"
)
def remove_material(
    material_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin)
):
    material = get_material_by_id(
        db,
        material_id
    )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    file_path = Path(
        material.file_path
    )

    if file_path.exists():

        try:
            os.remove(file_path)

        except OSError:
            pass

    delete_material(
        db,
        material_id
    )

    return {
        "message": "Material deleted successfully"
    }