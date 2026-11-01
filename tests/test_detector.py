"""
tests/test_detector.py
Unit tests for the ML layer — the three demo archetypes.
"""
from app.ml.detector import score_login


def _normal():
    return {
        "timestamp": "2026-11-03T11:45:00Z",
        "geo_velocity_kmh": 15,
        "is_new_device": False,
        "is_new_country": False,
        "failed_attempts": 0,
        "session_duration_s": 1800,
    }


def _impossible_travel():
    return {
        "timestamp": "2026-11-03T03:14:00Z",
        "geo_velocity_kmh": 980,
        "is_new_device": True,
        "is_new_country": True,
        "failed_attempts": 4,
        "session_duration_s": 12,
    }


def _off_hours_weekend():
    return {
        "timestamp": "2026-11-07T02:00:00Z",  # Saturday 2 AM
        "geo_velocity_kmh": 30,
        "is_new_device": True,
        "is_new_country": False,
        "failed_attempts": 2,
        "session_duration_s": 45,
    }


def test_normal_not_anomalous():
    r = score_login(_normal())
    assert r["is_anomaly"] is False
    assert r["risk_score"] < 0.4


def test_impossible_travel_is_anomalous():
    r = score_login(_impossible_travel())
    assert r["is_anomaly"] is True
    assert r["risk_score"] > 0.5
    assert r["feature_contributions"]["geo_velocity_kmh"] > 0.3


def test_weekend_attack_is_anomalous():
    r = score_login(_off_hours_weekend())
    assert r["is_anomaly"] is True
    assert r["risk_score"] > 0.5
    # The weekend fix must be observable
    assert r["feature_contributions"]["is_weekend"] > 0.0
    assert r["feature_contributions"]["is_new_device"] > 0.1


def test_contributions_sum_to_one():
    r = score_login(_normal())
    total = sum(r["feature_contributions"].values())
    assert 0.99 <= total <= 1.01