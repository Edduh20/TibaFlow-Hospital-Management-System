from sklearn.metrics import classification_report
from src.utils.logger import logger

def evaluate_classifier(model, X_test, y_test):
    preds = model.predict(X_test)
    logger.info("Report:\n" + classification_report(y_test, preds))
    return preds


