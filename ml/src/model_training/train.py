"""Train and save the best model."""
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from src.utils.logger import logger
from src.utils.helpers import save_object

def train(X_train, y_train, X_test, y_test, params: dict = {}):
    logger.info("Training model...")
    model = RandomForestClassifier(
        n_estimators=params.get("n_estimators", 100),
        max_depth=params.get("max_depth", 10),
        random_state=42,
    )
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    logger.info(f"Accuracy: {acc:.4f}")
    save_object("models/best_model.pkl", model)
    return model, acc
