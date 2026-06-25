"""Compute metrics and generate reports."""
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, r2_score
from src.utils.logger import logger
import numpy as np

def evaluate_classifier(model, X_test, y_test):
    preds = model.predict(X_test)
    logger.info("Report:\n" + classification_report(y_test, preds))
    return preds

def evaluate_regressor(model, X_test, y_test):
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    logger.info(f"RMSE: {rmse:.4f} | R2: {r2:.4f}")
    return preds
