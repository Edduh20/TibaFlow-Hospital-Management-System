from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.prediction.predict import predict
# from src.rag.pipeline import answer_question

app = FastAPI(title="ML + RAG API", version="0.2.0")

@app.get("/")
def root():
    return {"status": "ok", "message": "ML + RAG API is running"}


class PredictionRequest(BaseModel):
    symptoms:str

@app.post("/predict")
def predict_endpoint(request: PredictionRequest):
    result = predict(request.symptoms)
    return result


# class RAGRequest(BaseModel):
#     question: str

# @app.post("/rag/query")
# def rag_query(request: RAGRequest):
#     try:
#         result = answer_question(request.question)
#         return {
#             "answer": result["answer"],
#             "sources": result["sources"],
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
