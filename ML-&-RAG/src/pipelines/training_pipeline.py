from src.data_ingestion.collect_data import ingest_csv
from src.data_transformation.preprocess import  transform
from src.model_training.train import train
from src.model_evaluation.evaluate import evaluate_classifier
from src.utils.logger import logger

def run_ml_pipeline():
    logger.info("Starting training pipeline...")
    train_df = ingest_csv("data/processed/train/Training.csv")
    X_train, X_test, y_train, y_test, le = transform(train_df, "prognosis")
    best_model, model_scores = train(X_train, y_train, X_test, y_test)
    preds = evaluate_classifier(best_model, X_test, y_test)
    logger.info(f"Pipeline complete. Scores: {model_scores}")

if __name__ == "__main__":
    run_ml_pipeline()