"""Versioned HTTP request and response contracts."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    manufacturer: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=150)
    registration_year: int = Field(ge=1900, le=2100)
    mileage_km: float = Field(ge=0, le=2_000_000)
    trim: str | None = Field(default=None, max_length=500)
    fuel: str | None = Field(default=None, max_length=100)
    transmission: str | None = Field(default=None, max_length=100)
    drivetrain: str | None = Field(default=None, max_length=50)
    repair_history: bool | None = None
    prefecture: str | None = Field(default=None, max_length=100)

    @field_validator("manufacturer", "model")
    @classmethod
    def required_text_must_not_be_blank(cls, value):
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class PredictionResponse(BaseModel):
    estimated_fair_price_jpy: int
    expected_range_low_jpy: int
    expected_range_high_jpy: int
    target_interval_coverage: float
    model_reference_year: int
    valuation_basis: Literal["advertised_vehicle_price"]


class HealthResponse(BaseModel):
    status: Literal["ok", "not_ready"]
    environment: str
    version: str


class ModelInfoResponse(BaseModel):
    model_name: str
    model_reference_year: int
    model_features: list[str]
    feature_count: int
    target_interval_coverage: float
    valuation_basis: str
    artifact_sha256: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Any | None = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody
