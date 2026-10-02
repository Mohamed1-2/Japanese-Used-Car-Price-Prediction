import pandas as pd

from src.ui_options import build_ui_options


def test_vehicle_options_only_include_observed_configuration_for_year():
    data = pd.DataFrame([
        {"manufacturer":"トヨタ", "model":"プリウス", "registration_year":2018,
         "fuel":"ハイブリッド", "transmission":"CVT", "drivetrain":"2WD",
         "prefecture":"東京都", "quality_status":"ready", "vehicle_price_jpy":2_000_000},
        {"manufacturer":"トヨタ", "model":"プリウス", "registration_year":2023,
         "fuel":"プラグインハイブリッド", "transmission":"CVT", "drivetrain":"2WD",
         "prefecture":"大阪府", "quality_status":"ready", "vehicle_price_jpy":4_000_000},
        {"manufacturer":"トヨタ", "model":"プリウス", "registration_year":2018,
         "fuel":"電気自動車", "transmission":"AT", "drivetrain":"4WD",
         "prefecture":"東京都", "quality_status":"failed", "vehicle_price_jpy":2_000_000},
    ])

    options = build_ui_options(data)
    year_2018 = options["vehicle_options"]["トヨタ"]["プリウス"]["2018"]

    assert year_2018 == {
        "fuel": ["ハイブリッド"],
        "transmission": ["CVT"],
        "drivetrain": ["2WD"],
    }
    assert sorted(options["vehicle_options"]["トヨタ"]["プリウス"]) == ["2018", "2023"]


def test_manufacturer_aliases_are_canonicalized_without_merging_amg():
    data = pd.DataFrame([
        {"manufacturer":"AMG", "model":"GT", "registration_year":2020,
         "fuel":"ガソリン", "transmission":"AT", "drivetrain":"2WD",
         "prefecture":"東京都", "quality_status":"ready", "vehicle_price_jpy":10_000_000},
    ])

    options = build_ui_options(data)

    assert options["manufacturer_to_models"] == {"メルセデスAMG": ["GT"]}
