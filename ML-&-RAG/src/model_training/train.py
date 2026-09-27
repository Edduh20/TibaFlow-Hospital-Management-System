from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from src.utils.logger import logger
from src.utils.helpers import save_object

def train(X_train, y_train, X_test, y_test):
    logger.info("Training model...")
    models = {"RandomForest": RandomForestClassifier(random_state=42),
              "KNB": KNeighborsClassifier(),
              "LinearRegression": LogisticRegression(random_state=42),
              "XGB": XGBClassifier(random_state=42)}
    model_scores = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        model_scores[name] = model.score(X_test, y_test)

    best_model_name = max(model_scores, key=model_scores.get)
    best_model = models[best_model_name]
    logger.info(f"Best model: {best_model_name} with accuracy {model_scores[best_model_name]:.4f}")
    save_object("models/Random-Forest-Model.joblib", best_model)

    return best_model, model_scores


