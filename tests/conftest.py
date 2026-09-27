from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


class FakePredictor:
    def model_info(self):
        return {
            "model_name": "test-model",
            "model_reference_year": 2026,
            "model_features": ["manufacturer", "model"],
            "feature_count": 2,
            "target_interval_coverage": 0.8,
            "valuation_basis": "advertised_vehicle_price",
            "artifact_sha256": "0" * 64,
        }

    def predict(self, payload):
        if payload["registration_year"] > 2027:
            raise ValueError("registration_year is outside the supported range")
        return {
            "estimated_fair_price_jpy": 3_000_000,
            "expected_range_low_jpy": 2_400_000,
            "expected_range_high_jpy": 3_750_000,
            "target_interval_coverage": 0.8,
            "model_reference_year": 2026,
            "valuation_basis": "advertised_vehicle_price",
        }


@pytest.fixture
def client():
    settings = Settings(
        environment="test",
        model_path=Path("unused.joblib"),
        ui_options_path=Path("unused.json"),
    )
    application = create_app(
        settings=settings,
        predictor=FakePredictor(),
        options={"manufacturer_to_models": {"トヨタ": ["アルファード"]}},
    )
    with TestClient(application) as test_client:
        yield test_client
