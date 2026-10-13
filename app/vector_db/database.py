# Kept for backwards compatibility. The vector store now lives in
# app/ai/vector_store.py so there is only one Chroma client.
from app.ai.llm import embed as create_embedding  # noqa: F401
from app.ai.vector_store import (  # noqa: F401
    add_document,
    search_documents,
    collection,
)
