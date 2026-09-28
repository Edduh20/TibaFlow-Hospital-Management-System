from dotenv import load_dotenv
from src.rag.pipeline import build_index

load_dotenv()

if __name__ == "__main__":
    build_index("data/processed/knowledge_base")