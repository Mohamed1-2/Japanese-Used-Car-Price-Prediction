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

    # These six records are known make/model parse conflicts in the current
    # Carsensor/GooNet snapshot. They would otherwise expose impossible cars
    # (for example a Honda Sienta) in the public form. Keep the rule explicit
    # and scoped to UI choices; do not silently rewrite model training rows.
    known_make_model_conflicts = {
        ("ホンダ", "シエンタ"),
        ("ホンダ", "ヴォクシー"),
        ("トヨタ", "ノート"),
        ("トヨタ", "ルークス"),
        ("日産", "スペーシアカスタム"),
        ("国産車その他", "デイズ"),
    }
    pairs = pd.MultiIndex.from_arrays(
        [eligible["manufacturer"], eligible["model"]]
    )
    eligible = eligible.loc[~pairs.isin(known_make_model_conflicts)]
    # Generic parser buckets aren't useful as customer-facing makes.
    eligible = eligible.loc[
        ~eligible["manufacturer"].isin({"輸入車その他", "国産車その他"})
    ]

    vehicle_options = {}
    grouped = eligible.groupby(
        ["manufacturer", "model", "registration_year"], sort=True, observed=True
    )
    for (make, model, year), rows in grouped:
        vehicle_options.setdefault(make, {}).setdefault(model, {})[str(year)] = {
            "fuel": _values(rows["fuel"]),
            "transmission": _values(rows["transmission"]),
            "drivetrain": _values(rows["drivetrain"]),
            "trim": _values(rows["trim"]),
        }

    make_to_models = {
        make: sorted(models) for make, models in vehicle_options.items()
    }
    return {
        "schema_version": 2,
        "manufacturer_to_models": make_to_models,
        "vehicle_options": vehicle_options,
        "model_display_names": {
            "シトロエンDS21 1年保証付き": "DS21",
        },
        "fuel_values": _values(eligible["fuel"]),
        "transmission_values": _values(eligible["transmission"]),
        "drivetrain_values": _values(eligible["drivetrain"]),
        "prefecture_values": _values(eligible["prefecture"]),
    }


def validate_prediction_options(payload, options):
    """Reject unsupported vehicle/configuration values before model inference."""
    if not options or "vehicle_options" not in options:
        # Backward compatibility while an older options artifact is deployed.
        make_models = (options or {}).get("manufacturer_to_models", {})
        if payload.get("manufacturer") not in make_models:
            raise ValueError("Choose a manufacturer from the available options.")
        if payload.get("model") not in make_models[payload["manufacturer"]]:
            raise ValueError("Choose a model available for that manufacturer.")
        return

    vehicle_options = options["vehicle_options"]
    make = payload.get("manufacturer")
    model = payload.get("model")
    by_year = vehicle_options.get(make, {}).get(model)
    if not by_year:
        raise ValueError("Choose a model available for that manufacturer.")

    try:
        year_key = str(int(payload.get("registration_year")))
    except (TypeError, ValueError):
        raise ValueError("Choose a registration year from the available options.") from None
    config = by_year.get(year_key)
    if not config:
        raise ValueError("That registration year is not listed for this model.")

    for field in ("fuel", "transmission", "drivetrain", "trim"):
        value = payload.get(field)
        if value not in (None, "") and value not in config.get(field, []):
            raise ValueError(f"Choose a listed {field.replace('_', ' ')} for this vehicle.")

    prefecture = payload.get("prefecture")
    if prefecture not in (None, "") and prefecture not in options.get("prefecture_values", []):
        raise ValueError("Choose a prefecture from the available options.")
