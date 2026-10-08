"""
vector.py - Compatibility bridge.
Delegates to modular `retriever.py` and `ingest.py`.
"""
from retriever import get_vector_store, get_retriever
from config import DEFAULT_TOP_K

vector_store = get_vector_store()
retriever = get_retriever(k=DEFAULT_TOP_K)