import os
import sys

import numpy as np
import pandas as pd
from dataclasses import dataclass
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.exception import CustomException
from src.logger import logger
from src.utils import ARTIFACT_ROOT, save_object

NUMERICAL_FEATURES = ["Age", "KM", "HP", "MetColor", "Automatic", "CC", "Doors", "Weight"]
CATEGORICAL_FEATURES = ["FuelType"]


@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path: str = os.path.join(ARTIFACT_ROOT, "preprocessor.pkl")


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self) -> ColumnTransformer:
        """Build the reusable preprocessing recipe (fitted later on TRAIN data only)."""
        try:
            numerical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )
            categorical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                ]
            )

            preprocessor = ColumnTransformer(
                transformers=[
                    ("numerical_pipeline", numerical_pipeline, NUMERICAL_FEATURES),
                    ("categorical_pipeline", categorical_pipeline, CATEGORICAL_FEATURES),
                ]
            )
            logger.info("Preprocessor recipe created")
            return preprocessor
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_data_transformation(
        self, train_path: str, test_path: str
    ) -> tuple[np.ndarray, np.ndarray, str]:
        """Fit preprocessor on TRAIN, transform both sets, persist it. Returns arrays + path."""
        try:
            target_column = "Price"

            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logger.info(f"Loaded train={train_df.shape}, test={test_df.shape}")

            input_feature_train_df = train_df.drop(columns=[target_column])
            target_feature_train_df = train_df[target_column]
            input_feature_test_df = test_df.drop(columns=[target_column])
            target_feature_test_df = test_df[target_column]

            preprocessor = self.get_data_transformer_object()

            # Fit ONLY on train. Never peek at the test set - that leaks information.
            input_feature_train_arr = preprocessor.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessor.transform(input_feature_test_df)

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]
            logger.info("Transformation done: train/test arrays built")

            save_object(self.data_transformation_config.preprocessor_obj_file_path, preprocessor)
            return train_arr, test_arr, self.data_transformation_config.preprocessor_obj_file_path

        except Exception as e:
            raise CustomException(e, sys) from e