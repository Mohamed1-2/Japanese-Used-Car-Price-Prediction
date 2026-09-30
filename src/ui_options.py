"""Build frontend choices from vehicle combinations observed in training data."""

import re
import unicodedata

import pandas as pd


UNKNOWN = "__UNKNOWN__"
MIN_TARGET_JPY = 30_000
MAX_TARGET_JPY = 100_000_000

MANUFACTURER_CANONICAL_MAP = {
    "AMG": "メルセデスAMG",
    "メルセデスAMG": "メルセデスAMG",
    "メルセデス・マイバッハ": "メルセデス・マイバッハ",
    "メルセデスマイバッハ": "メルセデス・マイバッハ",
    "MINI": "MINI",
    "ミニ": "MINI",
}


def normalize_text(value):
    if pd.isna(value):
        return UNKNOWN
    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = re.sub(r"\s+", " ", text)
    return UNKNOWN if text in {"", "-", "−", "'-", "不明", "nan", "None"} else text


def canonicalize_manufacturer(value):
    normalized = normalize_text(value)
    return MANUFACTURER_CANONICAL_MAP.get(normalized, normalized)


def _values(series):
    return sorted(value for value in series.dropna().map(normalize_text).unique() if value != UNKNOWN)


def build_ui_options(data):
    """Return global fallbacks plus choices indexed by make, model, and year."""
    required = {
        "manufacturer", "model", "registration_year", "fuel", "transmission",
        "drivetrain", "prefecture", "quality_status", "vehicle_price_jpy",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    eligible = data.loc[
        data["quality_status"].eq("ready")
        & data["vehicle_price_jpy"].between(MIN_TARGET_JPY, MAX_TARGET_JPY)
    ].copy()
    eligible["manufacturer"] = eligible["manufacturer"].map(canonicalize_manufacturer)
    eligible["model"] = eligible["model"].map(normalize_text)
    eligible["registration_year"] = pd.to_numeric(
        eligible["registration_year"], errors="coerce"
    )
    eligible = eligible.loc[
        eligible["manufacturer"].ne(UNKNOWN)
        & eligible["model"].ne(UNKNOWN)
        & eligible["registration_year"].between(1900, 2100)
    ]
    eligible["registration_year"] = eligible["registration_year"].astype(int)

    vehicle_options = {}
    grouped = eligible.groupby(
        ["manufacturer", "model", "registration_year"], sort=True, observed=True
    )
    for (make, model, year), rows in grouped:
        vehicle_options.setdefault(make, {}).setdefault(model, {})[str(year)] = {
            "fuel": _values(rows["fuel"]),
            "transmission": _values(rows["transmission"]),
            "drivetrain": _values(rows["drivetrain"]),
        }

    make_to_models = {
        make: sorted(models) for make, models in vehicle_options.items()
    }
    return {
        "schema_version": 2,
        "manufacturer_to_models": make_to_models,
        "vehicle_options": vehicle_options,
        "fuel_values": _values(eligible["fuel"]),
        "transmission_values": _values(eligible["transmission"]),
        "drivetrain_values": _values(eligible["drivetrain"]),
        "prefecture_values": _values(eligible["prefecture"]),
    }
