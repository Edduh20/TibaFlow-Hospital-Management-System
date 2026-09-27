import pandas as pd
from src.utils.logger import logger

def ingest_csv(file_path: str) -> pd.DataFrame:
    logger.info(f"Ingesting data from {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {df.shape[0]} rows x {df.shape[1]} cols")
    return df
