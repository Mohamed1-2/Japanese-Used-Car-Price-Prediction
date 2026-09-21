import os
import sys

import dill
from sklearn.model_selection import cross_val_score

from src.exception import CustomException
from src.logger import logger

# Central location where every stage writes its artifacts (train.csv, model.pkl, ...)
ARTIFACT_ROOT = os.path.join(os.getcwd(), "artifacts")


def save_object(file_path: str, obj) -> None:
    """Persist any Python object (pipeline, model, ...) using dill."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            dill.dump(obj, f)
        logger.info(f"Saved object -> {file_path}")
    except Exception as e:
        raise CustomException(e, sys) from e


def load_object(file_path: str):
    """Load a previously saved dill object back into memory."""
    try:
        with open(file_path, "rb") as f:
            return dill.load(f)
    except Exception as e:
        raise CustomException(e, sys) from e


def evaluate_models(models: dict, X_train, y_train, cv: int = 5, scoring: str = "r2") -> dict:
    """Run cross-validation scoring for every model and return {name: mean_score}."""
    results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
        results[name] = scores.mean()
        logger.info(f"{name}: CV {scoring} = {scores.mean():.4f} (+/- {scores.std():.4f})")
    return results