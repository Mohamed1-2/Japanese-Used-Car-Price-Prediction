"""FastAPI application factory and versioned inference endpoints."""

from contextlib import asynccontextmanager
import json
import logging
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings
from app.logging_config import configure_logging
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
)
from src.pipeline.fair_price_inference import FairPricePredictor
from src.ui_options import validate_prediction_options

logger = logging.getLogger("fair_price_api")


def _error_response(request, status_code, code, message, details=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


def create_app(settings=None, predictor=None, options=None):
    settings = settings or Settings.from_env()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(application):
        application.state.ready = False
        application.state.predictor = predictor or FairPricePredictor(
            settings.model_path
        )
        if options is not None:
            application.state.ui_options = options
        elif settings.ui_options_path.is_file():
            with settings.ui_options_path.open(encoding="utf-8") as options_file:
                application.state.ui_options = json.load(options_file)
        else:
            application.state.ui_options = None
        application.state.ready = True
        logger.info(
            "model_loaded",
            extra={"status_code": 200},
        )
        yield
        application.state.ready = False

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Estimate the advertised listing price and calibrated market range "
            "for Japanese used cars."
        ),
        lifespan=lifespan,
    )
    application.state.settings = settings
    static_dir = Path(__file__).resolve().parent / "static"
    application.mount("/static", StaticFiles(directory=static_dir), name="static")

    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )

    @application.middleware("http")
    async def request_context(request, call_next):
        request.state.request_id = request.headers.get("X-Request-ID") or str(
            uuid4()
        )
        started = perf_counter()
        response = await call_next(request)
        duration_ms = round((perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request.state.request_id
        logger.info(
            "request_completed",
            extra={
                "request_id": request.state.request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return _error_response(
            request,
            422,
            "validation_error",
            "Request validation failed.",
            jsonable_encoder(exc.errors()),
        )

    @application.exception_handler(HTTPException)
    async def http_error(request, exc):
        detail = exc.detail
        message = detail if isinstance(detail, str) else "Request failed."
        return _error_response(
            request,
            exc.status_code,
            "http_error",
            message,
            None if isinstance(detail, str) else detail,
        )

    @application.exception_handler(Exception)
    async def unhandled_error(request, exc):
        logger.exception(
            "unhandled_error",
            extra={"request_id": getattr(request.state, "request_id", None)},
        )
        return _error_response(
            request,
            500,
            "internal_error",
            "An internal error occurred.",
        )

    @application.get("/", include_in_schema=False)
    def root():
        return FileResponse(static_dir / "index.html")

    @application.get("/health", response_model=HealthResponse, tags=["operations"])
    def health(request: Request):
        return {
            "status": "ok" if request.app.state.ready else "not_ready",
            "environment": settings.environment,
            "version": settings.app_version,
        }

    @application.get(
        "/v1/model-info",
        response_model=ModelInfoResponse,
        tags=["operations"],
    )
    def model_info(request: Request):
        return request.app.state.predictor.model_info()

    @application.get("/v1/options", tags=["metadata"])
    def prediction_options(request: Request):
        if request.app.state.ui_options is None:
            raise HTTPException(
                status_code=404,
                detail="Prediction options are not available.",
            )
        return request.app.state.ui_options

    @application.post(
        "/v1/predict",
        response_model=PredictionResponse,
        responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
        tags=["predictions"],
    )
    def predict(payload: PredictionRequest, request: Request):
        try:
            validate_prediction_options(
                payload.model_dump(exclude_none=True),
                request.app.state.ui_options,
            )
            return request.app.state.predictor.predict(
                payload.model_dump(exclude_none=True)
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return application


app = create_app()
