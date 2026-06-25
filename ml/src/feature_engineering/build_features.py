"""Create and encode features."""
import pandas as pd
from src.utils.logger import logger

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building features...")
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    logger.info(f"Features ready. Shape: {df.shape}")
    return df
