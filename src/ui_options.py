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

BMW_MODEL_ENGLISH_NAMES = {
    "1シリーズ": "1 Series",
    "1シリーズクーペ": "1 Series Coupe",
    "2シリーズ": "2 Series",
    "2シリーズアクティブツアラー": "2 Series Active Tourer",
    "2シリーズカブリオレ": "2 Series Convertible",
    "2シリーズクーペ": "2 Series Coupe",
    "2シリーズグランクーペ": "2 Series Gran Coupe",
    "2シリーズグランツアラー": "2 Series Gran Tourer",
    "3.0CS": "3.0 CS",
    "3シリーズ": "3 Series",
    "3シリーズクーペ": "3 Series Coupe",
    "3シリーズグランツーリスモ": "3 Series Gran Turismo",
    "3シリーズセダン": "3 Series Sedan",
    "3シリーズツーリング": "3 Series Touring",
    "4シリーズ": "4 Series",
    "4シリーズカブリオレ": "4 Series Convertible",
    "4シリーズクーペ": "4 Series Coupe",
    "4シリーズグランクーペ": "4 Series Gran Coupe",
    "5シリーズ": "5 Series",
    "5シリーズツーリング": "5 Series Touring",
    "6シリーズ": "6 Series",
    "6シリーズグランクーペ": "6 Series Gran Coupe",
    "6シリーズグランツーリスモ": "6 Series Gran Turismo",
    "7シリーズ": "7 Series",
    "8シリーズ": "8 Series",
    "8シリーズカブリオレ": "8 Series Convertible",
    "8シリーズグランクーペ": "8 Series Gran Coupe",
    "M2": "M2",
    "M2クーペ": "M2 Coupe",
    "M2コンペティション": "M2 Competition",
    "M3": "M3",
    "M3セダン": "M3 Sedan",
    "M3ツーリング": "M3 Touring",
    "M4": "M4",
    "M4クーペ": "M4 Coupe",
    "M5": "M5",
    "M5ツーリング": "M5 Touring",
    "M8": "M8",
    "X1": "X1",
    "X2": "X2",
    "X3": "X3",
    "X3 M": "X3 M",
    "X4": "X4",
    "X4 M": "X4 M",
    "X5": "X5",
    "X6": "X6",
    "X6 M": "X6 M",
    "X7": "X7",
    "XM": "XM",
    "Z4": "Z4",
    "i3": "i3",
    "i4": "i4",
    "i5": "i5",
    "i5ツーリング": "i5 Touring",
    "i7": "i7",
    "i8": "i8",
    "iX": "iX",
    "iX1": "iX1",
    "iX2": "iX2",
    "iX3": "iX3",
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


def _realistic_drivetrain(row):
    """Prefer explicit manufacturer/vehicle evidence over inconsistent scraped tags."""
    make = row["manufacturer"]
    model = row["model"]
    text = " ".join(
        value for value in (normalize_text(row.get("trim")), normalize_text(row.get("title")))
        if value != UNKNOWN
    ).casefold()

    # BMW's official Z4 specifications list rear-wheel drive, including M40i.
    if make == "BMW" and model == "Z4":
        return "2WD"

    four_wheel_markers = (
        "4wd", "4x4", "awd", "xdrive", "xドライブ", "quattro", "4matic",
        "4motion", "e-four", "e-4orce", "sh-awd", "allgrip", "四輪駆動",
    )
    two_wheel_markers = ("2wd", "sdrive", "前輪駆動", "後輪駆動")
    if any(marker in text for marker in four_wheel_markers):
        return "4WD"
    if any(marker in text for marker in two_wheel_markers):
        return "2WD"
    return normalize_text(row.get("drivetrain"))


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
    # A make name in the model field is a parser placeholder, not a useful
    # customer-facing vehicle identity (for example, BMW / BMW).
    eligible = eligible.loc[
        eligible["manufacturer"].str.casefold()
        != eligible["model"].str.casefold()
    ].copy()
    eligible["drivetrain_option"] = eligible.apply(_realistic_drivetrain, axis=1)
    eligible["trim_option"] = eligible["trim"].map(normalize_text)

    vehicle_options = {}
    grouped = eligible.groupby(
        ["manufacturer", "model", "registration_year"], sort=True, observed=True
    )
    for (make, model, year), rows in grouped:
        trim_options = {}
        known_trim_rows = rows.loc[rows["trim_option"].ne(UNKNOWN)]
        for trim, trim_rows in known_trim_rows.groupby("trim_option", sort=True):
            trim_options[trim] = {
                "fuel": _values(trim_rows["fuel"]),
                "transmission": _values(trim_rows["transmission"]),
                "drivetrain": _values(trim_rows["drivetrain_option"]),
            }
        vehicle_options.setdefault(make, {}).setdefault(model, {})[str(year)] = {
            "fuel": _values(rows["fuel"]),
            "transmission": _values(rows["transmission"]),
            "drivetrain": _values(rows["drivetrain_option"]),
            "trim": sorted(trim_options),
            "trim_options": trim_options,
        }

    make_to_models = {
        make: sorted(models) for make, models in vehicle_options.items()
    }
    return {
        "schema_version": 3,
        "manufacturer_to_models": make_to_models,
        "vehicle_options": vehicle_options,
        "model_display_names": {
            "シトロエンDS21 1年保証付き": "DS21",
        },
        "model_english_names": {
            model: label
            for model, label in BMW_MODEL_ENGLISH_NAMES.items()
            if model in {value for models in make_to_models.values() for value in models}
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

    selected_trim = payload.get("trim")
    validated_config = config.get("trim_options", {}).get(selected_trim, config)
    for field in ("fuel", "transmission", "drivetrain"):
        value = payload.get(field)
        if value not in (None, "") and value not in validated_config.get(field, []):
            raise ValueError(f"Choose a listed {field.replace('_', ' ')} for this vehicle.")

    if selected_trim not in (None, "") and selected_trim not in config.get("trim", []):
        raise ValueError("Choose a listed trim for this vehicle.")

    prefecture = payload.get("prefecture")
    if prefecture not in (None, "") and prefecture not in options.get("prefecture_values", []):
        raise ValueError("Choose a prefecture from the available options.")
