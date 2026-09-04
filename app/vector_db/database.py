import os
import chromadb
from mistralai.client import Mistral


# =========================
# MISTRAL CONFIGURATION
# =========================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise RuntimeError(
        "MISTRAL_API_KEY environment variable is not set."
    )

mistral_client = Mistral(
    api_key=MISTRAL_API_KEY
)

MISTRAL_EMBED_MODEL = "mistral-embed"


# =========================
# CHROMA DATABASE
# =========================

client = chromadb.PersistentClient(
    path="./chroma_data"
)

collection = client.get_or_create_collection(
    name="study_materials"
)


# =========================
# CREATE EMBEDDING
# =========================

def create_embedding(
    text: str
):

    response = mistral_client.embeddings.create(
        model=MISTRAL_EMBED_MODEL,
        inputs=[text]
    )

    return response.data[0].embedding


# =========================
# ADD DOCUMENT
# =========================

def add_document(
    document_id: str,
    text: str,
    metadata: dict
):

    embedding = create_embedding(
        text
    )

    collection.add(
        ids=[document_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )


# =========================
# SEARCH DOCUMENTS
# =========================

def search_documents(
    query: str,
    number_of_results: int = 5
):

    query_embedding = create_embedding(
        query
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=number_of_results
    )

    return results