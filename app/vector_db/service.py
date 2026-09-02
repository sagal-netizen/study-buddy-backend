from pathlib import Path

from pypdf import PdfReader
from docx import Document
from pptx import Presentation
from openpyxl import load_workbook

from app.vector_db.database import add_document


# =========================
# TEXT EXTRACTION
# =========================

def extract_text(file_path: str) -> str:

    path = Path(file_path)

    extension = path.suffix.lower()

    # -------------------------
    # PDF
    # -------------------------

    if extension == ".pdf":

        reader = PdfReader(
            str(path)
        )

        text = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

        return "\n".join(text)


    # -------------------------
    # DOC / DOCX
    # -------------------------

    if extension in [".doc", ".docx"]:

        document = Document(
            str(path)
        )

        text = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():
                text.append(
                    paragraph.text
                )

        return "\n".join(text)


    # -------------------------
    # PPT / PPTX
    # -------------------------

    if extension in [".ppt", ".pptx"]:

        presentation = Presentation(
            str(path)
        )

        text = []

        for slide in presentation.slides:

            for shape in slide.shapes:

                if hasattr(
                    shape,
                    "text"
                ):

                    if shape.text.strip():

                        text.append(
                            shape.text
                        )

        return "\n".join(text)


    # -------------------------
    # XLS / XLSX
    # -------------------------

    if extension in [".xls", ".xlsx"]:

        workbook = load_workbook(
            filename=str(path),
            read_only=True,
            data_only=True
        )

        text = []

        for sheet in workbook.worksheets:

            for row in sheet.iter_rows(
                values_only=True
            ):

                row_text = " ".join(
                    str(cell)
                    for cell in row
                    if cell is not None
                )

                if row_text.strip():

                    text.append(
                        row_text
                    )

        return "\n".join(text)


    # -------------------------
    # TXT / CSV
    # -------------------------

    if extension in [
        ".txt",
        ".csv"
    ]:

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )


    return ""


# =========================
# SPLIT TEXT
# =========================

def split_text(
    text: str,
    chunk_size: int = 1000
):

    text = text.strip()

    if not text:
        return []

    chunks = []

    for i in range(
        0,
        len(text),
        chunk_size
    ):

        chunk = text[
            i:i + chunk_size
        ].strip()

        if chunk:
            chunks.append(
                chunk
            )

    return chunks


# =========================
# INDEX MATERIAL
# =========================

def index_material(
    material_id: int,
    file_path: str,
    filename: str,
    course_id: int
):

    text = extract_text(
        file_path
    )

    if not text.strip():
        return 0


    chunks = split_text(
        text
    )


    for index, chunk in enumerate(
        chunks
    ):

        document_id = (
            f"material_{material_id}"
            f"_chunk_{index}"
        )

        add_document(
            document_id=document_id,
            text=chunk,
            metadata={
                "material_id": material_id,
                "course_id": course_id,
                "filename": filename,
                "chunk_index": index
            }
        )


    return len(chunks)