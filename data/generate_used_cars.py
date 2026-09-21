"""
Generate a realistic synthetic Japanese used-car dataset.

The schema mirrors the well-known "Used Cars (Japan)" regression benchmark:
    Price     (target, JPY)     - Metropolitan Area used-car price
    Age       (years in service)
    KM        (kilometers driven)
    FuelType  (Petrol / Diesel / CNG / LPG)
    HP        (horsepower)
    MetColor  (metallic paint: 0/1)
    Automatic (automatic gearbox: 0/1)
    CC        (engine capacity, cc)
    Doors     (number of doors)
    Weight    (kg)

Prices follow a realistic non-linear relationship with the features plus
Gaussian noise, so gradient-boosted tree models clearly outperform linear ones.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_STATE = 42

FUEL_ENGINE_FACTOR = {
    "Petrol": 0.0,
    "Diesel": 0.35,
    "CNG": -0.18,
    "LPG": -0.12,
}

FUEL_WEIGHTS = [0.62, 0.22, 0.08, 0.08]


def generate(df_size: int = 1200) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)

    n = df_size
    age = np.clip(rng.negative_binomial(6.0, 0.30, size=n), 1, 45)
    km = np.clip(age * rng.uniform(8000, 16000, size=n)
                 + rng.uniform(-5000, 5000, size=n), 0, 350_000)
    hp = np.clip(np.round(rng.uniform(58, 320, size=n)).astype(int), 40, 380)
    cc = np.clip(
        np.round((hp - 40) * 12.5 + rng.normal(0, 140, size=n)),
        500, 4700,
    ).astype(int)
    doors = rng.choice([2, 3, 4, 5], size=n, p=[0.18, 0.06, 0.62, 0.14])
    weight = np.clip(
        np.full(n, 1050.0) * (1 + rng.uniform(-0.15, 0.15, size=n))
        + cc * 0.82,
        600, 3500,
    ).round(1)
    met_color = rng.integers(0, 2, size=n)
    automatic = rng.choice([0, 1], size=n, p=[0.45, 0.55])
    fuel = rng.choice(list(FUEL_ENGINE_FACTOR), size=n, p=FUEL_WEIGHTS)

    # Synthesize (log-space) price
    base = 260_000 + np.full(n, 0.0)
    base += 3150.0 * (200.0 - age)                 # newer cars cost far more
    base -= km * 0.045                            # wear and tear
    base += np.full(n, 1e-6) + (base * 0).astype(float)
    log_price = np.log(np.maximum(base, 1_000))
    log_price += hp * 0.0035
    log_price += np.vectorize(FUEL_ENGINE_FACTOR.get)(fuel) * 0.6
    log_price += automatic * 0.10
    log_price -= (cc - 1300.0) * 0.00012
    log_price += (weight - 1300.0) * 0.00005
    log_price += np.clip((km / 20_000.0) - 3.0, 0, None) * 0.0  # stylistic
    log_price += rng.normal(0.0, 0.13, size=n)

    price = np.exp(log_price).round(-2)
    price = np.maximum(price, 50_000)

    df = pd.DataFrame(
        {
            "Price": price,
            "Age": age,
            "KM": km.round(0),
            "FuelType": fuel,
            "HP": hp,
            "MetColor": met_color,
            "Automatic": automatic,
            "CC": cc,
            "Doors": doors,
            "Weight": weight,
        }
    )
    return df


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "used_cars_data.csv"
    df = generate()
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows -> {out_path}")