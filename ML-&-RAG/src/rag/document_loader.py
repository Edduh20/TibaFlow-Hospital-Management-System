from src.utils.logger import logger
from langchain_community.document_loaders import DirectoryLoader, TextLoader

def load_documents(dir_path: str = "data/processed/knowledge_base") -> list:
    logger.info(f"Loading directory: {dir_path}")
    loader = DirectoryLoader(
        dir_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"})

    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents")
    return documents



