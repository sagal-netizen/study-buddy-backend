import os

import chromadb
from dotenv import load_dotenv
from mistralai.client import Mistral
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


# ==============================
# DATABASE CONFIGURATION
# ==============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==============================
# FILE UPLOAD CONFIGURATION
# ==============================

UPLOAD_DIRECTORY = os.getenv(
    "UPLOAD_DIRECTORY",
    "./uploads"
)

os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# ==============================
# MISTRAL CONFIGURATION
# ==============================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise RuntimeError("MISTRAL_API_KEY environment variable is not set.")

mistral_client = Mistral(
    api_key=MISTRAL_API_KEY
)

MISTRAL_EMBED_MODEL = "mistral-embed"


# ==============================
# CHROMA VECTOR DATABASE
# ==============================

CHROMA_PERSIST_DIRECTORY = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    "./chroma_data"
)

client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIRECTORY
)

collection = client.get_or_create_collection(
    name="study_materials"
)


# ==============================
# EMBEDDINGS
# ==============================

def create_embedding(text: str):
    response = mistral_client.embeddings.create(
        model=MISTRAL_EMBED_MODEL,
        inputs=[text]
    )

    return response.data[0].embedding


# ==============================
# ADD DOCUMENT
# ==============================

def add_document(
    document_id: str,
    text: str,
    metadata: dict
):
    embedding = create_embedding(text)

    collection.add(
        ids=[document_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )


# ==============================
# SEARCH DOCUMENTS
# ==============================

def search_documents(
    query: str,
    number_of_results: int = 5
):
    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=number_of_results
    )

    return results