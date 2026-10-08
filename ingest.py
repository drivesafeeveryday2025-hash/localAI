import sys
from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import (
    RESOURCE_DIR,
    DB_DIR,
    EMBEDDING_MODEL,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    SUPPORTED_EXTENSIONS,
    configure_windows_encoding
)

configure_windows_encoding()

def get_embedding_model() -> OllamaEmbeddings:
    """Returns initialized OllamaEmbeddings instance."""
    return OllamaEmbeddings(model=EMBEDDING_MODEL)

def load_and_chunk_documents(data_dir: Path = RESOURCE_DIR) -> list[Document]:
    """
    Recursively scans data_dir and all subdirectories/children folders for .txt and .md files,
    splitting them into chunks with hierarchical metadata.
    """
    all_chunks = []
    
    if not data_dir.exists():
        print(f"Directory {data_dir} does not exist.")
        return all_chunks

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS
    )

    # Use rglob to recursively scan all subfolders and nested files
    for file_path in data_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Relative path displays category subfolder, e.g. "Cars/yaris.md"
                rel_path = file_path.relative_to(data_dir).as_posix()

                docs = splitter.create_documents(
                    texts=[content],
                    metadatas=[{"source": rel_path, "filename": file_path.name}]
                )
                all_chunks.extend(docs)
                print(f"Loaded '{rel_path}': {len(docs)} chunks created.")
            except Exception as e:
                print(f"Error reading '{file_path}': {e}")

    return all_chunks

def ingest_single_file(file_path: Path, data_dir: Path = RESOURCE_DIR) -> int:
    """
    Splits and ingests a single file into the existing Chroma vector store without full rebuild.
    Returns the count of added chunks.
    """
    if not file_path.exists() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS
    )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        rel_path = file_path.relative_to(data_dir).as_posix() if file_path.is_relative_to(data_dir) else file_path.name

        docs = splitter.create_documents(
            texts=[content],
            metadatas=[{"source": rel_path, "filename": file_path.name}]
        )

        if not docs:
            return 0

        embeddings = get_embedding_model()
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(DB_DIR),
            embedding_function=embeddings,
        )
        vector_store.add_documents(docs)
        print(f"Incrementally added {len(docs)} chunks for '{rel_path}'.")
        return len(docs)
    except Exception as e:
        print(f"Error incrementally ingesting '{file_path}': {e}")
        return 0

def build_vector_store(force_rebuild: bool = False) -> Chroma:
    """Ingests documents into Chroma vector store."""
    embeddings = get_embedding_model()
    
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

    current_count = vector_store._collection.count()
    if current_count == 0 or force_rebuild:
        if force_rebuild and current_count > 0:
            print("Force rebuild requested. Resetting collection...")
            vector_store.delete_collection()
            vector_store = Chroma(
                collection_name=COLLECTION_NAME,
                persist_directory=str(DB_DIR),
                embedding_function=embeddings,
            )
        
        print(f"Recursively ingesting documents from {RESOURCE_DIR}...")
        documents = load_and_chunk_documents(RESOURCE_DIR)
        if documents:
            vector_store.add_documents(documents)
            print(f"Successfully added {len(documents)} document chunks into ChromaDB.")
        else:
            print("No documents found in resource folder.")
    else:
        print(f"Database already contains {current_count} chunks. Skipping re-ingestion.")

    return vector_store

if __name__ == "__main__":
    force = "--rebuild" in sys.argv
    build_vector_store(force_rebuild=force)
