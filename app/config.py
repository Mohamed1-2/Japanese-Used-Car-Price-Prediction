"""Environment-driven API configuration."""

from dataclasses import dataclass
import os
from pathlib import Path

from src.pipeline.fair_price_inference import DEFAULT_ARTIFACT


def _origins_from_env(value):
    return tuple(origin.strip() for origin in value.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "Japanese Used-Car Fair Price API"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    model_path: Path = DEFAULT_ARTIFACT
    ui_options_path: Path = (
        DEFAULT_ARTIFACT.parent / "ui_options.json"
    )
    cors_origins: tuple[str, ...] = ()

    @classmethod
    def from_env(cls):
        return cls(
            app_name=os.getenv("APP_NAME", cls.app_name),
            app_version=os.getenv("APP_VERSION", cls.app_version),
            environment=os.getenv("APP_ENV", cls.environment),
            log_level=os.getenv("LOG_LEVEL", cls.log_level).upper(),
            model_path=Path(os.getenv("MODEL_PATH", str(DEFAULT_ARTIFACT))),
            ui_options_path=Path(
                os.getenv(
                    "UI_OPTIONS_PATH",
                    str(DEFAULT_ARTIFACT.parent / "ui_options.json"),
                )
            ),
            cors_origins=_origins_from_env(os.getenv("CORS_ORIGINS", "")),
        )
