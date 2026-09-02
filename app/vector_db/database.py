import chromadb
import ollama


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

    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )

    return response["embedding"]


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
