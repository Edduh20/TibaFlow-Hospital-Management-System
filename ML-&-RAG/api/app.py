from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.prediction.predict import predict
from src.rag.pipeline import answer_question

app = FastAPI(title="DiagnosAI API", version="0.2.0")

@app.get("/")
def root():
    return {"status": "ok", "message": "ML + RAG API is running"}


class PredictionRequest(BaseModel):
    symptoms:str

@app.post("/predict")
def predict_endpoint(request: PredictionRequest):
    result = predict(request.symptoms)
    return result

class RAGRequest(BaseModel):
    question: str

@app.post("/answer_question")
def answer_question_endpoint(request: RAGRequest):
    result = answer_question(request.question)
    return result


