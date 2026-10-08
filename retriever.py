import urllib.request
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from config import (
    DB_DIR,
    EMBEDDING_MODEL,
    COLLECTION_NAME,
    DEFAULT_TOP_K,
    configure_windows_encoding
)

configure_windows_encoding()

def check_ollama_alive(host: str = "http://localhost:11434") -> bool:
    """Checks if the local Ollama service is reachable."""
    try:
        req = urllib.request.urlopen(f"{host}/api/version", timeout=3)
        return req.status == 200
    except Exception:
        return False

def get_vector_store() -> Chroma:
    """Connects to the persistent ChromaDB collection without re-indexing."""
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

def get_retriever(k: int = DEFAULT_TOP_K):
    """Returns a retriever object configured for Top-K semantic search."""
    vs = get_vector_store()
    return vs.as_retriever(search_kwargs={"k": k})

