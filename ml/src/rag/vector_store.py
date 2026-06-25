"""
Vector Store
------------
Build, save, and load a FAISS vector index from document chunks.
"""
import os
from langchain.vectorstores import FAISS
from src.utils.logger import logger

FAISS_INDEX_PATH = "artifacts/faiss_index"


def build_vector_store(chunks: list, embeddings) -> FAISS:
    logger.info("Building FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    logger.info(f"Vector store built with {len(chunks)} chunks")
    return vector_store


def save_vector_store(vector_store: FAISS, path: str = FAISS_INDEX_PATH):
    os.makedirs(path, exist_ok=True)
    vector_store.save_local(path)
    logger.info(f"Vector store saved to {path}")


def load_vector_store(embeddings, path: str = FAISS_INDEX_PATH) -> FAISS:
    logger.info(f"Loading vector store from {path}")
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
