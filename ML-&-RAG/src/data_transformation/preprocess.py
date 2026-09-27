import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from src.utils.logger import logger
from src.utils.helpers import save_object

def transform(df: pd.DataFrame, target_col: str, test_size: float = 0.2):
    X = df.drop(target_col, axis=1)

    y = df[target_col]

    le = LabelEncoder()
    y = le.fit_transform(y)


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    logger.info(f"Saving Label-Encoder...")
    save_object("models/Label-Encoder.joblib", le)
    return X_train, X_test, y_train, y_test, le
