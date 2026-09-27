def valid_payload():
    return {
        "manufacturer": "トヨタ",
        "model": "アルファード",
        "registration_year": 2021,
        "mileage_km": 42_000,
        "fuel": "ガソリン",
    }


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "environment": "test",
        "version": "1.0.0",
    }
    assert response.headers["X-Request-ID"]


def test_prediction(client):
    response = client.post("/v1/predict", json=valid_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["estimated_fair_price_jpy"] == 3_000_000
    assert body["expected_range_low_jpy"] < body["estimated_fair_price_jpy"]
    assert body["expected_range_high_jpy"] > body["estimated_fair_price_jpy"]


def test_validation_rejects_missing_manufacturer(client):
    payload = valid_payload()
    payload.pop("manufacturer")
    response = client.post("/v1/predict", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_validation_rejects_unknown_fields(client):
    payload = valid_payload()
    payload["vehicle_price_jpy"] = 1
    response = client.post("/v1/predict", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_model_dependent_validation(client):
    payload = valid_payload()
    payload["registration_year"] = 2028
    response = client.post("/v1/predict", json=payload)
    assert response.status_code == 422
    assert "outside the supported range" in response.json()["error"]["message"]


def test_model_info_does_not_expose_artifact_path(client):
    response = client.get("/v1/model-info")
    assert response.status_code == 200
    body = response.json()
    assert body["model_name"] == "test-model"
    assert "artifact_path" not in body


def test_prediction_options(client):
    response = client.get("/v1/options")
    assert response.status_code == 200
    assert response.json()["manufacturer_to_models"]["トヨタ"] == ["アルファード"]
