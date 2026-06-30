from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.prediction.predict import predict
from src.rag.pipeline import answer_question

app = FastAPI(title="ML + RAG API", version="0.2.0")


# ── Classic ML ────────────────────────────────────────────
class PredictionRequest(BaseModel):
    # Replace with your actual feature fields
    feature1: float
    feature2: float

@app.get("/")
def root():
    return {"status": "ok", "message": "ML + RAG API is running"}

@app.post("/predict")
def predict_endpoint(request: PredictionRequest):
    result = predict(request.dict())
    return {"prediction": result}


# ── RAG ───────────────────────────────────────────────────
class RAGRequest(BaseModel):
    question: str

@app.post("/rag/query")
def rag_query(request: RAGRequest):
    try:
        result = answer_question(request.question)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
