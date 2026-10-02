"""Create the production UI option artifact from the model training dataset."""

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui_options import build_ui_options


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data", type=Path, default=Path("data/raw/japan-cars-csv_new.csv")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("notebook/artifacts/ui_options.json")
    )
    return parser.parse_args()


def main():
    args = parse_args()
    options = build_ui_options(pd.read_csv(args.data, low_memory=False))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(options, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    configurations = sum(
        len(years)
        for models in options["vehicle_options"].values()
        for years in models.values()
    )
    print(f"Saved {args.output}")
    print(f"Manufacturers: {len(options['manufacturer_to_models']):,}")
    print(f"Make/model/year combinations: {configurations:,}")


if __name__ == "__main__":
    main()
