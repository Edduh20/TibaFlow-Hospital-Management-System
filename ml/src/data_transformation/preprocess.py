import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def transform(df: pd.DataFrame, target_col: str, test_size: float = 0.2):
    X = df.drop(target_col, axis=1)

    y = df[target_col]

    le = LabelEncoder()
    y = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    return X_train, X_test, y_train, y_test, le
