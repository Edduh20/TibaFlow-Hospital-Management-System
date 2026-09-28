from src.utils.logger import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents: list, chunk_size: int = 1000, chunk_overlap: int = 100) -> list:
    logger.info(f"Chunking {len(documents)} documents (size={chunk_size}, overlap={chunk_overlap})")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")
    return chunks