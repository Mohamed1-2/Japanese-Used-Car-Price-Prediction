# Used Car Price Prediction (Japan)

A clean, production-style ML pipeline that predicts the price (JPY) of Japanese used
cars from raw attributes.

## Project structure

```
ML_Project/
├── data/
│   ├── generate_used_cars.py      # creates the local dataset (reproducible)
│   └── raw/
│       └── used_cars_data.csv     # source CSV read by ingestion
├── artifacts/                     # (generated at runtime, gitignored)
│   ├── train.csv / test.csv       # split produced by ingestion
│   ├── preprocessor.pkl           # fitted preprocessing pipeline (dill)
│   └── model.pkl                  # best fitted model (dill)
├── src/
│   ├── logger.py                  # run-scoped logging
│   ├── exception.py               # CustomException with file+line context
│   ├── utils.py                   # shared helpers + artifact root
│   ├── components/
│   │   ├── data_ingestion.py      # read CSV -> train/test split -> save
│   │   ├── data_transformation.py # fit preprocessor on train -> save pkl
│   │   └── model_trainer.py       # CV model selection -> save best model
│   └── pipeline/
│       └── train_pipeline.py      # orchestrates the 3 stages
├── requirements.txt
├── setup.py
└── .gitignore
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Train

```bash
python -m src.pipeline.train_pipeline
```

This logs every step under `logs/` and prints the final test-set metrics
(R² / MAE / RMSE) for the best of several regressors.

## Roadmap (next phases)

- Prediction pipeline: load the saved `preprocessor.pkl` + `model.pkl` to price new cars
- Flask API endpoint to serve predictions over HTTP
- Unit tests for each pipeline stage
- Hyperparameter tuning + experiment tracking (MLflow)
- CI/CD + Docker packaging
- Unit tests for each pipeline stage
- Hyperparameter tuning + experiment tracking (MLflow)
- CI/CD + Docker packaging
## Fair-price notebook model

Run `notebook/01_used_car_fair_price_EDA.ipynb`, then `notebook/02_used_car_fair_price_model_training.ipynb` from the project virtual environment. The training notebook compares CatBoost, LightGBM, XGBoost, and a median baseline using the same split. It exports the selected model to `notebook/artifacts/fair_price_model.joblib`.

Use the same feature engineering in an application through `src.pipeline.fair_price_inference.predict_fair_price`:

```python
from src.pipeline.fair_price_inference import predict_fair_price

result = predict_fair_price({
    "manufacturer": "トヨタ",
    "model": "アルファード",
    "registration_year": 2021,
    "mileage_km": 42000,
})
```

The prediction estimates advertised vehicle price, not a completed sale price. The interval is calibrated to 80% nominal coverage on the source snapshot. Validate on later listings before public deployment, monitor errors by vehicle segment, and retrain as the market changes. Load model artifacts only from trusted sources.

## GitHub and MLOps workflow

See [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md) for the latest evaluation. Follow [`docs/GITHUB_MLOPS_PUSH.md`](docs/GITHUB_MLOPS_PUSH.md) for the reviewed branch, pull-request, and model-promotion workflow. Raw datasets and trained artifacts belong in versioned S3 locations and are intentionally excluded from Git.
