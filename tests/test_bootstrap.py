from pathlib import Path

import pytest

from app.bootstrap import download_verified, parse_s3_uri, sha256_file


class FakeS3:
    def __init__(self, content):
        self.content = content

    def download_file(self, bucket, key, filename):
        assert bucket == "model-bucket"
        assert key == "models/model.joblib"
        Path(filename).write_bytes(self.content)


def test_parse_s3_uri():
    assert parse_s3_uri("s3://model-bucket/models/model.joblib") == (
        "model-bucket",
        "models/model.joblib",
    )


@pytest.mark.parametrize("uri", ["", "https://bucket/key", "s3://bucket", "s3:///key"])
def test_parse_s3_uri_rejects_invalid_values(uri):
    with pytest.raises(ValueError):
        parse_s3_uri(uri)


def test_download_verified_is_atomic_and_checks_hash(tmp_path):
    content = b"trusted model artifact"
    expected = "ce2f8091a5f013bf7aa3ed9b986a3d57a9c52a2f47db37e444ca702fda95ab02"
    destination = tmp_path / "model.joblib"
    download_verified(
        FakeS3(content),
        "s3://model-bucket/models/model.joblib",
        destination,
        expected,
    )
    assert destination.read_bytes() == content
    assert sha256_file(destination) == expected


def test_download_rejects_bad_checksum(tmp_path):
    destination = tmp_path / "model.joblib"
    with pytest.raises(ValueError, match="checksum mismatch"):
        download_verified(
            FakeS3(b"wrong"),
            "s3://model-bucket/models/model.joblib",
            destination,
            "0" * 64,
        )
    assert not destination.exists()
