"""
Document Loader
---------------
Load and chunk documents from PDFs, text files, or directories.
"""
from langchain.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.utils.logger import logger


def load_pdf(file_path: str) -> list:
    logger.info(f"Loading PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} pages")
    return documents


def load_text(file_path: str) -> list:
    logger.info(f"Loading text file: {file_path}")
    loader = TextLoader(file_path)
    return loader.load()


def load_directory(dir_path: str, glob: str = "**/*.pdf") -> list:
    logger.info(f"Loading directory: {dir_path}")
    loader = DirectoryLoader(dir_path, glob=glob)
    return loader.load()


def chunk_documents(documents: list, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    logger.info(f"Chunking {len(documents)} documents (size={chunk_size}, overlap={chunk_overlap})")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")
    return chunks
