"""
Single place for every call to the AI provider (chat + embeddings).

Currently using Mistral.

To switch to Ollama later, only this file needs to change. The OLLAMA_*
values are kept in .env / .env.example for that purpose:

    OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, OLLAMA_EMBED_MODEL

NOTE: embeddings from different models have different dimensions, so after
switching provider, point CHROMA_COLLECTION_NAME (app/ai/vector_store.py)
at a new collection and re-upload / re-index the study materials.
"""

import os

from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise RuntimeError("MISTRAL_API_KEY environment variable is not set.")

_client = Mistral(api_key=MISTRAL_API_KEY)

CHAT_MODEL = "mistral-small-latest"
EMBED_MODEL = "mistral-embed"


def chat(prompt: str) -> str:
    """Send a single user prompt and return the model's text answer."""
    response = _client.chat.complete(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


def embed(text: str) -> list[float]:
    """Return the embedding vector for a piece of text."""
    response = _client.embeddings.create(
        model=EMBED_MODEL,
        inputs=[text],
    )

    return response.data[0].embedding
