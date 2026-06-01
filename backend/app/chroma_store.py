from pathlib import Path

import chromadb
from chromadb.api import ClientAPI

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "chroma"
COLLECTION_NAME = "summarag"

_client: ClientAPI | None = None


def get_chroma_client() -> ClientAPI:
    global _client
    if _client is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(DATA_DIR))
    return _client


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)
