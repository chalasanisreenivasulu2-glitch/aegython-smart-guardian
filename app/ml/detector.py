"""
app/ml/detector.py
Isolation Forest based login anomaly detector for Smart Login Guardian.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime, timezone

from app.ml.data_generator import FEATURES, generate_baseline

_MODEL: IsolationForest | None = None
_BASELINE: pd.DataFrame | None = None
_MEANS: pd.Series | None = None
_STDS: pd.Series | None = None


def train_model(force: bool = False) -> None:
    """Train (or retrain) the Isolation Forest on synthetic baseline data."""
    global _MODEL, _BASELINE, _MEANS, _STDS
    if _MODEL is not None and not force:
        return

    df = generate_baseline()          # single source of truth — no local copy
    _BASELINE = df.copy()
    _MEANS = df.mean()
    _STDS = df.std().replace(0, 1.0)

    X = df[FEATURES].values
    _MODEL = IsolationForest(
        n_estimators=200,
        contamination=0.02,
        random_state=42,
        n_jobs=-1,
    )
    _MODEL.fit(X)


def _build_feature_row(payload: dict) -> pd.DataFrame:
    """Convert an incoming login payload into a FEATURES DataFrame row."""
    ts = payload.get("timestamp")
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if ts is None:
        ts = datetime.now(timezone.utc)

    return pd.DataFrame([{
        "hour_of_day": ts.hour,
        "day_of_week": ts.weekday(),
        "is_weekend": int(ts.weekday() >= 5),
        "geo_velocity_kmh": float(payload.get("geo_velocity_kmh", 0.0)),
        "is_new_device": int(bool(payload.get("is_new_device", False))),
        "is_new_country": int(bool(payload.get("is_new_country", False))),
        "failed_attempts": int(payload.get("failed_attempts", 0)),
        "session_duration_s": int(payload.get("session_duration_s", 0)),
    }])[FEATURES]


def _feature_contributions(row: pd.DataFrame) -> dict[str, float]:
    """
    Simple, transparent contribution score per feature:
    |z-score| against the baseline distribution, normalised to sum=1.
    """
    z = ((row.iloc[0] - _MEANS) / _STDS).abs()
    total = float(z.sum()) or 1.0
    return {feat: float(round(val / total, 4)) for feat, val in z.items()}


def score_login(payload: dict) -> dict:
    """
    Score a single login event.

    Returns:
        {
          "risk_score": float 0-1,
          "is_anomaly": bool,
          "feature_contributions": {...},
          "raw_decision": int
        }
    """
    train_model()
    row = _build_feature_row(payload)

    raw = float(_MODEL.decision_function(row.values)[0])
    pred = int(_MODEL.predict(row.values)[0])

    risk_score = float(np.clip(0.5 - raw, 0.0, 1.0))

    return {
        "risk_score": round(risk_score, 4),
        "is_anomaly": pred == -1,
        "feature_contributions": _feature_contributions(row),
        "raw_decision": pred,
    }


if __name__ == "__main__":
    # Smoke test — also reachable via `python -m app.ml.detector`
    train_model(force=True)
    normal = {
        "timestamp": "2026-11-03T11:45:00Z",
        "geo_velocity_kmh": 15,
        "is_new_device": False,
        "is_new_country": False,
        "failed_attempts": 0,
        "session_duration_s": 1800,
    }
    attack = {
        "timestamp": "2026-11-03T03:14:00Z",
        "geo_velocity_kmh": 980,
        "is_new_device": True,
        "is_new_country": True,
        "failed_attempts": 4,
        "session_duration_s": 12,
    }
    print("NORMAL:", score_login(normal))
    print("ATTACK:", score_login(attack))