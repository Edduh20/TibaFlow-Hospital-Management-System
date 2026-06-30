"""
Embeddings
----------
Generate vector embeddings using HuggingFace (free/local) or OpenAI.
"""
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from src.utils.logger import logger


def get_huggingface_embeddings(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Free, runs locally. Good default."""
    logger.info(f"Loading HuggingFace embeddings: {model_name}")
    return HuggingFaceEmbeddings(model_name=model_name)


def get_openai_embeddings(api_key: str = None):
    """Requires OPENAI_API_KEY in .env"""
    logger.info("Loading OpenAI embeddings")
    return OpenAIEmbeddings(openai_api_key=api_key)
