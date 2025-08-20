import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

def get_chroma_client():
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_directory,
        settings=ChromaSettings(
            anonymized_telemetry=False
        )
    )
    return client

def get_collection():
    client = get_chroma_client()
    try:
        collection = client.get_collection(name=settings.chroma_collection_name)
    except:
        collection = client.create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    return collection