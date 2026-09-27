import os
from langchain_qdrant import QdrantVectorStore
from src.utils.logger import logger

COLLECTION_NAME = "diagnosai_knowledge_base"

def build_vector_store(chunks: list, embeddings) -> QdrantVectorStore:
    logger.info("Building Qdrant vector store...")
    vector_store = QdrantVectorStore.from_documents(chunks,
                                                    embeddings,
                                                    url=os.getenv("QDRANT_URL"),
                                                    api_key=os.getenv("QDRANT_API_KEY"),
                                                    collection_name=COLLECTION_NAME)
    logger.info(f"Vector store built with {len(chunks)} chunks")
    return vector_store


def load_vector_store(embeddings) -> QdrantVectorStore:
    logger.info(f"Loading Qdrant vector store...")
    return QdrantVectorStore.from_existing_collection(embedding=embeddings,
                                                      url=os.getenv("QDRANT_URL"),
                                                      api_key=os.getenv("QDRANT_API_KEY"),
                                                      collection_name=COLLECTION_NAME)
