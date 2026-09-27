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

## Production API

Install the API dependencies and run locally:

```bash
python -m pip install -r requirements-api.txt
MODEL_PATH=notebook/artifacts/fair_price_model.joblib \
UI_OPTIONS_PATH=notebook/artifacts/ui_options.json \
uvicorn app.main:app --reload
```

OpenAPI is available at `http://localhost:8000/docs`. The primary endpoints are:

- `GET /health`
- `GET /v1/model-info`
- `GET /v1/options`
- `POST /v1/predict`

Example prediction:

```bash
curl -X POST http://localhost:8000/v1/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "manufacturer": "トヨタ",
    "model": "アルファード",
    "registration_year": 2021,
    "mileage_km": 42000,
    "fuel": "ガソリン"
  }'
```

Run tests:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

Run in Docker with the local model artifact mounted read-only:

```bash
docker compose up --build
```

## AWS deployment

AWS infrastructure is defined in `infra/terraform`. It provisions a versioned
private S3 model bucket, ECR repository, private ECS Fargate tasks, public
Application Load Balancer, CloudWatch logs, autoscaling, deployment rollback,
and a least-privilege GitHub OIDC role.

The production container downloads the approved model from S3 during startup
and verifies its SHA-256 before loading it. Long-lived AWS keys are not used by
GitHub Actions.

Initialize the infrastructure with the service disabled because ECR is empty:

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

Upload the approved model using the bucket name from `terraform output`:

```bash
cd ../..
python scripts/publish_model_artifacts.py \
  --bucket "$(terraform -chdir=infra/terraform output -raw artifact_bucket)" \
  --expected-model-sha256 ed2c5530e5a84cba1d108ce4d283d4424e4214deff9aa8b82f1de618a9eafd3c
```

Create a protected GitHub environment named `production`, then add the
repository variables returned by:

```bash
terraform -chdir=infra/terraform output -json github_repository_variables
```

Run the `Deploy API to AWS` workflow once to push the first image. Finally set
`service_enabled = true` in `terraform.tfvars` and run plan/apply again to start
the Fargate tasks.
