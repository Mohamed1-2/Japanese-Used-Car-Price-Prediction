"""Download approved model assets, verify them, then start the API."""

import hashlib
import logging
import os
from pathlib import Path
import sys
from urllib.parse import urlparse

import boto3

from app.logging_config import configure_logging

logger = logging.getLogger("fair_price_bootstrap")


def parse_s3_uri(uri):
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.lstrip("/"):
        raise ValueError(f"Invalid S3 URI: {uri}")
    return parsed.netloc, parsed.path.lstrip("/")


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_verified(s3_client, uri, destination, expected_sha256=None):
    destination = Path(destination)
    if destination.is_file():
        if not expected_sha256 or sha256_file(destination) == expected_sha256:
            logger.info("artifact_already_present")
            return destination

    bucket, key = parse_s3_uri(uri)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".download")
    try:
        s3_client.download_file(bucket, key, str(temporary))
        actual_sha256 = sha256_file(temporary)
        if expected_sha256 and actual_sha256 != expected_sha256:
            raise ValueError(
                "Downloaded model checksum mismatch: "
                f"expected {expected_sha256}, received {actual_sha256}"
            )
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    logger.info("artifact_downloaded")
    return destination


def prepare_assets(environ=None, s3_client=None):
    environ = environ or os.environ
    model_path = Path(
        environ.get("MODEL_PATH", "/models/fair_price_model.joblib")
    )
    model_uri = environ.get("MODEL_S3_URI", "").strip()
    model_sha256 = environ.get("MODEL_SHA256", "").strip().lower() or None

    options_path = Path(
        environ.get("UI_OPTIONS_PATH", "/models/ui_options.json")
    )
    options_uri = environ.get("UI_OPTIONS_S3_URI", "").strip()

    if not model_path.is_file() and not model_uri:
        raise FileNotFoundError(
            f"Model not found at {model_path} and MODEL_S3_URI is not configured."
        )

    if model_uri or options_uri:
        s3_client = s3_client or boto3.client("s3")
    if model_uri:
        download_verified(s3_client, model_uri, model_path, model_sha256)
    elif model_sha256 and sha256_file(model_path) != model_sha256:
        raise ValueError("Local model checksum does not match MODEL_SHA256.")

    if options_uri:
        download_verified(s3_client, options_uri, options_path)


def main():
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    prepare_assets()
    command = [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        os.getenv("PORT", "8000"),
        "--no-access-log",
    ]
    os.execvp(command[0], command)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("bootstrap_failed")
        sys.exit(1)
