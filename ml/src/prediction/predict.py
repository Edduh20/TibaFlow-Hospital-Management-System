"""Load saved model and run inference."""
import pandas as pd
from src.utils.helpers import load_object
from src.utils.logger import logger

def predict(input_data: dict) -> list:
    model = load_object("models/best_model.pkl")
    scaler = load_object("artifacts/scaler.pkl")
    df = pd.DataFrame([input_data])
    scaled = scaler.transform(df)
    return model.predict(scaled).tolist()
