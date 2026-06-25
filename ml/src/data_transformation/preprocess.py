"""Encode, scale, and split data."""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.utils.logger import logger
from src.utils.helpers import save_object

def transform(df: pd.DataFrame, target_col: str, test_size: float = 0.2):
    logger.info("Starting transformation...")
    X = df.drop(columns=[target_col])
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    save_object("artifacts/scaler.pkl", scaler)
    return X_train, X_test, y_train, y_test
