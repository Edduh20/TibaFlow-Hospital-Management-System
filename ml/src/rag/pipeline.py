"""
RAG Pipeline
------------
End-to-end: load docs → chunk → embed → index → query.
Run this once to build the index, then use the API for queries.
"""
import os
from dotenv import load_dotenv
from src.rag.document_loader import load_pdf, chunk_documents
from src.rag.embeddings import get_huggingface_embeddings
from src.rag.vector_store import build_vector_store, save_vector_store, load_vector_store
from src.rag.retriever import get_retriever
from src.rag.chain import get_huggingface_llm, build_rag_chain, query_chain
from src.utils.logger import logger

load_dotenv()


def build_index(doc_path: str):
    """Load a PDF, chunk it, embed it, and save the FAISS index."""
    documents = load_pdf(doc_path)
    chunks = chunk_documents(documents)
    embeddings = get_huggingface_embeddings()
    vector_store = build_vector_store(chunks, embeddings)
    save_vector_store(vector_store)
    logger.info("Index built and saved.")


def answer_question(question: str) -> dict:
    """Load the saved index and answer a question."""
    embeddings = get_huggingface_embeddings()
    vector_store = load_vector_store(embeddings)
    retriever = get_retriever(vector_store, k=4)
    llm = get_huggingface_llm(api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
    chain = build_rag_chain(retriever, llm)
    return query_chain(chain, question)


if __name__ == "__main__":
    # Step 1: Build index (run once)
    # build_index("data/raw/your_document.pdf")

    # Step 2: Query
    # result = answer_question("What is the main topic of the document?")
    # print(result["answer"])
    # print(result["sources"])
    pass
