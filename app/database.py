import os

import chromadb
import ollama

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Add it to your .env file before starting the server."
    )

# =========================================================
# OLLAMA CONFIGURATION
# =========================================================

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_CHAT_MODEL = os.getenv(
    "OLLAMA_CHAT_MODEL",
    "llama3.2"
)

OLLAMA_EMBED_MODEL = os.getenv(
    "OLLAMA_EMBED_MODEL",
    "nomic-embed-text"
)

# =========================================================
# CHROMADB CONFIGURATION
# =========================================================

CHROMA_PERSIST_DIRECTORY = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    "./chroma_data"
)

# =========================================================
# UPLOAD DIRECTORY CONFIGURATION
# =========================================================

UPLOAD_DIRECTORY = os.getenv(
    "UPLOAD_DIRECTORY",
    ""          # empty string = use default relative to backend root
)

# =========================================================
# SQLALCHEMY / POSTGRESQL
# =========================================================

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================================================
# CHROMADB
# =========================================================

client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIRECTORY
)

collection = client.get_or_create_collection(
    name="study_materials"
)


# =========================================================
# CREATE EMBEDDING
# =========================================================

def create_embedding(
    text: str
):
    ollama_client = ollama.Client(
        host=OLLAMA_BASE_URL
    )

    response = ollama_client.embeddings(
        model=OLLAMA_EMBED_MODEL,
        prompt=text
    )

    return response["embedding"]


# =========================================================
# ADD DOCUMENT TO CHROMADB
# =========================================================

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


# =========================================================
# SEARCH DOCUMENTS
# =========================================================

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
