import os
import sys
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    AdaBoostRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.tree import DecisionTreeRegressor

try:
    from catboost import CatBoostRegressor
except ImportError:  # pragma: no cover
    CatBoostRegressor = None

try:
    from xgboost import XGBRegressor
except ImportError:  # pragma: no cover
    XGBRegressor = None

from src.exception import CustomException
from src.logger import logger
from src.utils import ARTIFACT_ROOT, evaluate_models, save_object


@dataclass
class ModelTrainerConfig:
    trained_model_file_path: str = os.path.join(ARTIFACT_ROOT, "model.pkl")


class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        self.models = self._build_models()

    @staticmethod
    def _build_models() -> dict:
        """Candidate models. XGBoost/CatBoost only if importable (graceful degrade)."""
        models = {
            "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
            "ExtraTrees": ExtraTreesRegressor(n_estimators=200, random_state=42, n_jobs=-1),
            "GradientBoosting": GradientBoostingRegressor(random_state=42),
            "DecisionTree": DecisionTreeRegressor(random_state=42),
            "LinearRegression": LinearRegression(),
            "AdaBoost": AdaBoostRegressor(random_state=42),
        }
        if XGBRegressor is not None:
            models["XGBoost"] = XGBRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        if CatBoostRegressor is not None:
            models["CatBoost"] = CatBoostRegressor(random_state=42, verbose=0)
        return models

    def initiate_model_trainer(self, train_array: np.ndarray, test_array: np.ndarray) -> dict:
        try:
            X_train, y_train = train_array[:, :-1], train_array[:, -1]
            X_test, y_test = test_array[:, :-1], test_array[:, -1]

            # Cross-validated selection (on TRAIN only), then pick the winner
            model_scores = evaluate_models(self.models, X_train, y_train)
            best_model_name = max(model_scores, key=model_scores.get)

            best_model = self.models[best_model_name].fit(X_train, y_train)
            y_pred = best_model.predict(X_test)

            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))

            report = {
                "best_model": best_model_name,
                "cv_r2": round(model_scores[best_model_name], 4),
                "test_r2": round(r2, 4),
                "test_mae": round(mae, 2),
                "test_rmse": round(float(rmse), 2),
            }

            logger.info("=" * 60)
            logger.info("Model comparison (5-fold CV R2):")
            for name, score in sorted(model_scores.items(), key=lambda kv: kv[1], reverse=True):
                logger.info(f"  {name:>16s}: {score:.4f}")
            logger.info(f"Selected: {best_model_name}")
            logger.info(f"Test set -> R2={report['test_r2']}, MAE={report['test_mae']}, "
                        f"RMSE={report['test_rmse']}")
            logger.info("=" * 60)

            save_object(self.model_trainer_config.trained_model_file_path, best_model)
            return report

        except Exception as e:
            raise CustomException(e, sys) from e