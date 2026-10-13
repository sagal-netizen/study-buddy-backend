import os

import chromadb
from dotenv import load_dotenv

from app.ai.llm import embed

load_dotenv()


# =========================
# CHROMA VECTOR DATABASE
# =========================

CHROMA_PERSIST_DIRECTORY = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    "./chroma_data"
)

# Embedding dimensions differ per model. When the AI provider changes
# (see app/ai/llm.py), use a new collection name and re-index materials.
CHROMA_COLLECTION_NAME = "study_materials"

_client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIRECTORY
)

collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION_NAME
)


def add_document(
    document_id: str,
    text: str,
    metadata: dict
):
    # upsert so re-processing a material replaces its chunks
    # instead of failing on duplicate ids
    collection.upsert(
        ids=[document_id],
        documents=[text],
        embeddings=[embed(text)],
        metadatas=[metadata]
    )


def search_documents(
    query: str,
    number_of_results: int = 5,
    course_id: int | None = None
):
    # Chroma errors if the filter is applied to an empty collection
    # or n_results exceeds the stored count on some versions.
    total = collection.count()

    if total == 0:
        return {"documents": [[]], "metadatas": [[]]}

    options = {
        "query_embeddings": [embed(query)],
        "n_results": min(number_of_results, total),
    }

    if course_id is not None:
        options["where"] = {"course_id": course_id}

    return collection.query(**options)
