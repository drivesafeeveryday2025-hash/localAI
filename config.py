import sys
from pathlib import Path

# Project Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESOURCE_DIR = BASE_DIR / "resource"
RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = RESOURCE_DIR  # Alias for compatibility
DB_DIR = BASE_DIR / "chroma_langchain_db"

# Model Configurations
EMBEDDING_MODEL = "mxbai-embed-large"
LLM_MODEL = "qwen2.5-coder"
COLLECTION_NAME = "knowledge_base"

# Text Chunking Settings
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
CHUNK_SEPARATORS = ["\n# ", "\n## ", "\n### ", "\n\n", "\n", " ", ""]

# Retrieval Settings
DEFAULT_TOP_K = 5
SUPPORTED_EXTENSIONS = {".txt", ".md"}

# Ensure UTF-8 stdout encoding on Windows
def configure_windows_encoding():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

