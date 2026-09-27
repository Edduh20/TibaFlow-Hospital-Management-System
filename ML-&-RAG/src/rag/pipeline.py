from dotenv import load_dotenv

from src.rag.document_loader import load_documents
from src.rag.chunk import chunk_documents
from src.rag.embeddings import get_huggingface_embeddings
from src.rag.vector_store import build_vector_store, load_vector_store
from src.rag.retriever import get_retriever
from src.rag.chain import get_llms, build_rag_chain, query_chain
from src.utils.logger import logger

load_dotenv()

_cache = {
    "chain":None,
    "answers":{}
}

def build_index(doc_path: str):
    documents = load_documents(doc_path)
    chunks = chunk_documents(documents)
    embeddings = get_huggingface_embeddings()
    build_vector_store(chunks, embeddings)
    logger.info("Knowledge base indexed in Qdrant.")


def answer_question(question: str) -> dict:
    global _cache

    cleaned_question = question.lower().strip()

    if cleaned_question in _cache["answers"]:
        logger.info(f"Cache Found. Answer question: {cleaned_question}")
        return _cache["answers"][cleaned_question]

    embeddings = get_huggingface_embeddings()
    vector_store = load_vector_store(embeddings)
    retriever = get_retriever(vector_store, k=4)

    providers = ["gemini", "groq", "cohere", "mistral"]

    for provider in providers:
        try:
            logger.info(f"Trying {provider}...")

            llm = get_llms(provider)
            chain = build_rag_chain(retriever, llm)

            response = query_chain(chain, question)

            _cache["chain"] = chain
            _cache["answers"][cleaned_question] = response

            return response

        except Exception as e:
            if "429" in str(e):
                logger.warning(f"{provider} rate limit reached. Trying next provider...")
                continue

            logger.warning(f"{provider} failed: {e}")
            continue

    raise RuntimeError("All LLM providers failed.")


if __name__ == "__main__":

    pass
