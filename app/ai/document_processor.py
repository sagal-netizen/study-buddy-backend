from pathlib import Path

from pypdf import PdfReader
from docx import Document

from app.database import add_document


# =========================================================
# EXTRACT TEXT
# =========================================================

def extract_text(
    file_path: str,
    file_type: str
) -> str:

    extension = file_type.lower().lstrip(".")

    # PDF
    if extension == "pdf":

        reader = PdfReader(file_path)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    # DOCX
    if extension == "docx":

        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():
                paragraphs.append(
                    paragraph.text.strip()
                )

        return "\n".join(paragraphs)

    # TXT
    if extension == "txt":

        return Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore"
        )

    return ""


# =========================================================
# SPLIT TEXT INTO CHUNKS
# =========================================================

def chunk_text(
    text: str,
    words_per_chunk: int = 400
):

    words = text.split()

    chunks = []

    for start in range(
        0,
        len(words),
        words_per_chunk
    ):

        chunk = " ".join(
            words[
                start:start + words_per_chunk
            ]
        )

        if chunk.strip():
            chunks.append(chunk)

    return chunks


# =========================================================
# PROCESS DOCUMENT
# =========================================================

def process_document(
    file_path: str,
    file_type: str,
    material_id: int,
    course_id: int,
    chapter_id: int | None
):

    text = extract_text(
        file_path,
        file_type
    )

    if not text.strip():

        return {
            "success": False,
            "chunks": 0,
            "message": "No readable text found."
        }

    chunks = chunk_text(text)

    for index, chunk in enumerate(chunks):

        document_id = (
            f"material_{material_id}"
            f"_chunk_{index}"
        )

        metadata = {
            "material_id": material_id,
            "course_id": course_id,
            "chapter_id": chapter_id,
            "chunk_index": index,
            "file_type": file_type
        }

        add_document(
            document_id=document_id,
            text=chunk,
            metadata=metadata
        )

    return {
        "success": True,
        "chunks": len(chunks),
        "message": "Document embedded successfully."
    }