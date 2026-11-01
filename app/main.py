"""
app/main.py
FastAPI entry point for Smart Login Guardian.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.explainer import explain, suggested_action
from app.ml import score_login
from app.schemas import HealthResponse, LoginRequest, LoginResponse

app = FastAPI(
    title="Smart Login Guardian",
    description="Explainable login anomaly detection — AEGYTHON 2026",
    version=__version__,
)

# Streamlit runs on :8501, FastAPI on :8000 — allow the browser to cross over.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    """Liveness probe for Docker / load balancers."""
    return HealthResponse(status="ok", version=__version__)


@app.post("/analyze_login", response_model=LoginResponse, tags=["security"])
def analyze_login(req: LoginRequest) -> LoginResponse:
    """
    Score a login event, explain the result, and suggest a SOC action.
    """
    ts = req.timestamp or datetime.now(timezone.utc)

    payload = {
        "timestamp": ts.isoformat(),
        "geo_velocity_kmh": req.geo_velocity_kmh,
        "is_new_device": req.is_new_device,
        "is_new_country": req.is_new_country,
        "failed_attempts": req.failed_attempts,
        "session_duration_s": req.session_duration_s,
    }

    result = score_login(payload)
    reason = explain(result["risk_score"], result["feature_contributions"])

    return LoginResponse(
        user_id=req.user_id,
        risk_score=result["risk_score"],
        is_anomaly=result["is_anomaly"],
        explanation=reason,
        suggested_action=suggested_action(result["risk_score"]),
        feature_contributions=result["feature_contributions"],
    )