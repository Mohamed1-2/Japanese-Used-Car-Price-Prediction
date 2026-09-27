import pandas as pd

from src.pipeline.fair_price_inference import build_model_features


def test_manufacturer_aliases_match_training_taxonomy():
    raw = pd.DataFrame(
        [
            {
                "manufacturer": "AMG",
                "model": "Cクラス",
                "registration_year": 2022,
                "mileage_km": 30_000,
            },
            {
                "manufacturer": "ミニ",
                "model": "ミニクーパー",
                "registration_year": 2022,
                "mileage_km": 30_000,
            },
        ]
    )
    features = build_model_features(raw, reference_year=2026)
    assert features.loc[0, "manufacturer"] == "メルセデスAMG"
    assert features.loc[0, "manufacturer_group"] == "メルセデス・ベンツ"
    assert features.loc[1, "manufacturer"] == "MINI"
    assert features.loc[1, "manufacturer_group"] == "MINI"
