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