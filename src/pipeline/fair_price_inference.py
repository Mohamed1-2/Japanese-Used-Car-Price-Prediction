"""Production inference for the Japanese used-car listing-price model."""
from pathlib import Path
import re
import unicodedata
import joblib
import numpy as np
import pandas as pd

RAW_INPUT_FEATURES = ["manufacturer", "model", "trim", "registration_year", "mileage_km", "fuel", "transmission", "drivetrain", "repair_history", "prefecture"]
MANDATORY_INPUTS = ["manufacturer", "model", "registration_year", "mileage_km"]
DEFAULT_ARTIFACT = Path(__file__).resolve().parents[2] / "notebook" / "artifacts" / "fair_price_model.joblib"

MANUFACTURER_CANONICAL_MAP = {
    "AMG": "メルセデスAMG",
    "メルセデスAMG": "メルセデスAMG",
    "メルセデス・マイバッハ": "メルセデス・マイバッハ",
    "メルセデスマイバッハ": "メルセデス・マイバッハ",
    "MINI": "MINI",
    "ミニ": "MINI",
}

MANUFACTURER_GROUP_MAP = {
    "メルセデスAMG": "メルセデス・ベンツ",
    "メルセデス・マイバッハ": "メルセデス・ベンツ",
}

def normalize_text(value):
    """Return a stable string token for scraped/user categorical values."""
    if pd.isna(value):
        return "__UNKNOWN__"

    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = re.sub(r"\s+", " ", text)

    placeholders = {"", "-", "−", "'-", "不明", "nan", "None"}
    return "__UNKNOWN__" if text in placeholders else text


def normalize_fuel(value):
    """Collapse fuel synonyms into production-safe canonical values."""
    text = normalize_text(value)

    if text == "__UNKNOWN__":
        return text
    if "プラグイン" in text and "ハイブリッド" in text:
        return "phev"
    if "電気" in text or "EV" in text.upper():
        return "electric"
    if "ディーゼル" in text or "軽油" in text:
        return "diesel"
    if "ハイブリッド" in text:
        return "hybrid"
    if "ガソリン" in text:
        return "gasoline"
    if "水素" in text:
        return "hydrogen"
    return "other"


def normalize_transmission(value):
    """Convert detailed transmission strings into a stable family."""
    text = normalize_text(value).upper()

    if text == "__UNKNOWN__":
        return text
    if "CVT" in text:
        return "CVT"
    if "DCT" in text:
        return "DCT"
    # MT mode on an AT/CVT is not the same as a manual gearbox.
    if "AT" in text:
        return "AT"
    if "MT" in text:
        return "MT"
    return "other"


def extract_gear_count(value):
    """Extract a stated gear count such as 6 from 6AT, 6MT, or 6速."""
    text = normalize_text(value).upper()

    if text == "__UNKNOWN__":
        return np.nan

    match = re.search(r"(\d+)\s*(?:AT|MT|速)", text)
    return float(match.group(1)) if match else np.nan


def normalize_repair_history(value):
    """Preserve a true three-state concept: yes / no / unknown."""
    if pd.isna(value):
        return "__UNKNOWN__"

    if isinstance(value, (bool, np.bool_)):
        return "yes" if value else "no"

    text = str(value).strip().lower()

    if text in {"true", "1", "yes"}:
        return "yes"
    if text in {"false", "0", "no"}:
        return "no"

    return "__UNKNOWN__"


def canonicalize_manufacturer(value):
    """Merge source aliases while keeping AMG and Maybach distinct marques."""
    normalized = normalize_text(value)
    return MANUFACTURER_CANONICAL_MAP.get(normalized, normalized)


def manufacturer_group(value):
    """Return the corporate parent for hierarchical model context."""
    canonical = canonicalize_manufacturer(value)
    return MANUFACTURER_GROUP_MAP.get(canonical, canonical)



MODEL_FEATURES = [
    "manufacturer",
    "manufacturer_group",
    "model",
    "trim",
    "registration_year",
    "mileage_km",
    "vehicle_age",
    "log_mileage",
    "km_per_year",
    "fuel_clean",
    "transmission_simple",
    "gear_count",
    "manual_mode",
    "drivetrain",
    "repair_history_clean",
    "prefecture",
]

CATEGORICAL_FEATURES = [
    "manufacturer",
    "manufacturer_group",
    "model",
    "trim",
    "fuel_clean",
    "transmission_simple",
    "drivetrain",
    "repair_history_clean",
    "prefecture",
]


def build_model_features(raw_frame, reference_year):
    """
    Convert raw UI/scraper columns into exactly the features expected by the model.

    Parameters
    ----------
    raw_frame : pandas.DataFrame
        Must contain RAW_INPUT_FEATURES. Optional values may be null.
    reference_year : int
        Market year represented by the current trained model.

    Returns
    -------
    pandas.DataFrame
        Model-ready features in a fixed column order.
    """
    x = raw_frame.copy()

    # Guarantee that optional fields exist when this function is called
    # from an API payload that may omit them.
    for col in RAW_INPUT_FEATURES:
        if col not in x.columns:
            x[col] = np.nan

    # Apply the same manufacturer taxonomy used during training.
    x["manufacturer_group"] = x["manufacturer"].map(manufacturer_group)
    x["manufacturer"] = x["manufacturer"].map(canonicalize_manufacturer)

    # Clean remaining identity/location text without translating it.
    for col in ["model", "trim", "drivetrain", "prefecture"]:
        x[col] = x[col].map(normalize_text)

    # Canonical derived categoricals.
    x["fuel_clean"] = x["fuel"].map(normalize_fuel)
    x["transmission_simple"] = x["transmission"].map(normalize_transmission)
    x["repair_history_clean"] = x["repair_history"].map(
        normalize_repair_history
    )

    # Transmission-derived numerical indicators.
    x["gear_count"] = x["transmission"].map(extract_gear_count)
    x["manual_mode"] = x["transmission"].map(
        lambda value: int("MTモード" in normalize_text(value))
    )

    # Coerce user/scraped numerical inputs safely.
    x["registration_year"] = pd.to_numeric(
        x["registration_year"], errors="coerce"
    )
    x["mileage_km"] = pd.to_numeric(x["mileage_km"], errors="coerce")

    # Derived features.
    x["vehicle_age"] = (
        reference_year - x["registration_year"]
    ).clip(lower=0)

    x["log_mileage"] = np.log1p(x["mileage_km"].clip(lower=0))

    # Use at least one year in the denominator so nearly-new vehicles
    # do not create an infinite or undefined rate.
    x["km_per_year"] = (
        x["mileage_km"] / x["vehicle_age"].clip(lower=1)
    )

    return x[MODEL_FEATURES]

def predict_fair_price(payload, artifact_path=DEFAULT_ARTIFACT):
    """Return an estimated listing price and calibrated range in JPY."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    missing = [key for key in MANDATORY_INPUTS if payload.get(key) is None or payload.get(key) == ""]
    if missing:
        raise ValueError(f"Missing mandatory input(s): {missing}")
    artifact = joblib.load(artifact_path)
    year = int(artifact["reference_year"])
    try:
        registration_year = int(payload["registration_year"])
        mileage_km = float(payload["mileage_km"])
    except (TypeError, ValueError):
        raise ValueError("registration_year and mileage_km must be numeric") from None
    if not 1900 <= registration_year <= year + 1:
        raise ValueError("registration_year is outside the supported range")
    if not np.isfinite(mileage_km) or not 0 <= mileage_km <= 2_000_000:
        raise ValueError("mileage_km is outside the supported range")
    x = build_model_features(pd.DataFrame([payload]), reference_year=year)
    if x.columns.tolist() != artifact["model_features"]:
        raise ValueError("Feature schema differs from the trained model")
    point_log = float(artifact["model"].predict(x)[0])
    q = float(artifact["conformal_q_hat"])
    return {
        "estimated_fair_price_jpy": round(max(0, np.expm1(point_log))),
        "expected_range_low_jpy": round(max(0, np.expm1(point_log - q))),
        "expected_range_high_jpy": round(max(0, np.expm1(point_log + q))),
        "target_interval_coverage": 0.80,
        "model_reference_year": year,
        "valuation_basis": "advertised_vehicle_price",
    }
