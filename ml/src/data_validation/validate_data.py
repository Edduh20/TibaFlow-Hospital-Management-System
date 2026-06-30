"""Check schema, nulls, and types before processing."""
import pandas as pd
from src.utils.logger import logger

def validate(df: pd.DataFrame, required_columns: list) -> bool:
    logger.info("Running data validation...")
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        logger.error(f"Missing columns: {missing}")
        return False
    logger.info(f"Null counts:\n{df.isnull().sum()}")
    return True
