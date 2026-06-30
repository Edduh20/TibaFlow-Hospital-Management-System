"""
Retriever
---------
Similarity search over the FAISS index.
"""
from langchain.vectorstores import FAISS
from src.utils.logger import logger


def get_retriever(vector_store: FAISS, k: int = 4):
    """Return a retriever that fetches top-k similar chunks."""
    logger.info(f"Creating retriever (top_k={k})")
    return vector_store.as_retriever(search_kwargs={"k": k})


def similarity_search(vector_store: FAISS, query: str, k: int = 4) -> list:
    """Direct similarity search — returns raw document chunks."""
    logger.info(f"Searching for: '{query}'")
    results = vector_store.similarity_search(query, k=k)
    logger.info(f"Found {len(results)} results")
    return results
