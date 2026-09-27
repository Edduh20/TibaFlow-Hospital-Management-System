from langchain_community.vectorstores import FAISS
from src.utils.logger import logger


def get_retriever(vector_store: FAISS, k: int = 4):
    logger.info(f"Creating retriever (top_k={k})")
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k})


