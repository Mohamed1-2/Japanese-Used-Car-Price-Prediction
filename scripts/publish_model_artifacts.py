"""Upload an approved local model and UI metadata to the Terraform S3 bucket."""

import argparse
import hashlib
from pathlib import Path

import boto3


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def upload(s3, source, bucket, key, sha256):
    s3.upload_file(
        str(source),
        bucket,
        key,
        ExtraArgs={
            "ServerSideEncryption": "AES256",
            "Metadata": {"sha256": sha256},
        },
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("notebook/artifacts/fair_price_model.joblib"),
    )
    parser.add_argument(
        "--options",
        type=Path,
        default=Path("notebook/artifacts/ui_options.json"),
    )
    parser.add_argument(
        "--model-key",
        default="models/fair-price/v1/fair_price_model.joblib",
    )
    parser.add_argument(
        "--options-key",
        default="models/fair-price/v1/ui_options.json",
    )
    parser.add_argument("--expected-model-sha256", required=True)
    args = parser.parse_args()

    actual = sha256_file(args.model)
    if actual != args.expected_model_sha256:
        raise SystemExit(
            f"Model SHA-256 mismatch: expected {args.expected_model_sha256}, "
            f"received {actual}"
        )

    s3 = boto3.client("s3")
    upload(s3, args.model, args.bucket, args.model_key, actual)
    upload(
        s3,
        args.options,
        args.bucket,
        args.options_key,
        sha256_file(args.options),
    )
    print(f"Uploaded s3://{args.bucket}/{args.model_key}")
    print(f"Uploaded s3://{args.bucket}/{args.options_key}")


if __name__ == "__main__":
    main()
