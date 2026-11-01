"""
tests/test_api.py
Integration tests for the FastAPI endpoints.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_normal():
    r = client.post("/analyze_login", json={
        "user_id": "alice",
        "timestamp": "2026-11-03T11:45:00Z",
        "geo_velocity_kmh": 15,
        "is_new_device": False,
        "is_new_country": False,
        "failed_attempts": 0,
        "session_duration_s": 1800,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == "alice"
    assert body["is_anomaly"] is False
    assert body["suggested_action"] == "ALLOW"
    assert "explanation" in body


def test_analyze_impossible_travel():
    r = client.post("/analyze_login", json={
        "user_id": "alice",
        "timestamp": "2026-11-03T03:14:00Z",
        "geo_velocity_kmh": 980,
        "is_new_device": True,
        "is_new_country": True,
        "failed_attempts": 4,
        "session_duration_s": 12,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["is_anomaly"] is True
    assert body["risk_score"] > 0.5
    assert body["suggested_action"] in {"CHALLENGE_MFA", "BLOCK_AND_CHALLENGE_MFA"}
    assert "impossible travel" in body["explanation"].lower()


def test_analyze_weekend_offhours():
    r = client.post("/analyze_login", json={
        "user_id": "bob",
        "timestamp": "2026-11-07T02:00:00Z",
        "geo_velocity_kmh": 30,
        "is_new_device": True,
        "is_new_country": False,
        "failed_attempts": 2,
        "session_duration_s": 45,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["is_anomaly"] is True
    assert body["feature_contributions"]["is_weekend"] > 0.0