"""
RAG Chain
---------
Combines retriever + LLM into a question-answering chain.
Uses HuggingFace (free) by default. Swap in OpenAI if preferred.
"""
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceHub
from langchain.chat_models import ChatOpenAI
from src.utils.logger import logger


def get_huggingface_llm(repo_id: str = "google/flan-t5-base", api_token: str = None):
    """Free LLM via HuggingFace Hub. Needs HUGGINGFACEHUB_API_TOKEN in .env"""
    return HuggingFaceHub(
        repo_id=repo_id,
        huggingfacehub_api_token=api_token,
        model_kwargs={"temperature": 0.2, "max_length": 512},
    )


def get_openai_llm(api_key: str = None):
    """OpenAI ChatGPT. Needs OPENAI_API_KEY in .env"""
    return ChatOpenAI(openai_api_key=api_key, temperature=0.2)


def build_rag_chain(retriever, llm) -> RetrievalQA:
    logger.info("Building RAG chain...")
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    logger.info("RAG chain ready")
    return chain


def query_chain(chain: RetrievalQA, question: str) -> dict:
    logger.info(f"Querying: '{question}'")
    result = chain({"query": question})
    return {
        "answer": result["result"],
        "sources": [doc.metadata for doc in result["source_documents"]],
    }
