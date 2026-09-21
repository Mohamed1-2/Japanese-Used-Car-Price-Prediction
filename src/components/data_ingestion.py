import os
import sys

import pandas as pd
from dataclasses import dataclass
from sklearn.model_selection import train_test_split

from src.exception import CustomException
from src.logger import logger
from src.utils import ARTIFACT_ROOT

# Path to the source data file inside the repo (your "Local CSV in data/" choice)
RAW_DATA_PATH = os.path.join(os.getcwd(), "data", "raw", "used_cars_data.csv")


@dataclass
class DataIngestionConfig:
    """Files this stage will produce. Dataclass = zero boilerplate config holder."""

    train_data_path: str = os.path.join(ARTIFACT_ROOT, "train.csv")
    test_data_path: str = os.path.join(ARTIFACT_ROOT, "test.csv")
    raw_data_path: str = os.path.join(ARTIFACT_ROOT, "raw.csv")


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self) -> tuple[str, str]:
        """Read the CSV, split into train/test, write artifacts. Returns (train, test) paths."""
        try:
            df = pd.read_csv(RAW_DATA_PATH)
            logger.info(f"Loaded {len(df)} rows, {df.shape[1]} columns")

            # Never silently double-entries; check and drop duplicate rows
            df.drop_duplicates(inplace=True)
            logger.info(f"After dropping duplicates: {len(df)} rows")

            # Full-split records train vs test, and correct Pandas row-indexing
            df = df.sample(frac=1, random_state=42)

            train_set, test_set = train_test_split(
                df, test_size=0.20, random_state=42, stratify=None
            )
            logger.info(f"Train size: {train_set.shape[0]} | Test size: {test_set.shape[0]}")

            # Persist the three outputs (raw copy, train, test)
            df.to_csv(self.ingestion_config.raw_data_path, index=False)
            train_set.to_csv(self.ingestion_config.train_data_path, index=False)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False)
            logger.info("Ingestion finished and artifacts written")

            return self.ingestion_config.train_data_path, self.ingestion_config.test_data_path

        except Exception as e:
            raise CustomException(e, sys) from e