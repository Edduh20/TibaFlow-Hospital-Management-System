import os
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from src.utils.logger import logger


def get_huggingface_embeddings(model: str = "sentence-transformers/all-MiniLM-L6-v2"):
    logger.info(f"Loading HuggingFace embeddings: {model}")
    return HuggingFaceEndpointEmbeddings(model=model,
                                         huggingfacehub_api_token=os.getenv("HF_TOKEN"))


