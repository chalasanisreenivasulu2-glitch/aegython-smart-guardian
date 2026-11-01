"""
app/schemas.py
Pydantic models for the Smart Login Guardian API.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """A single login event submitted for risk scoring."""

    user_id: str = Field(..., description="Free-form user label (no PII).")
    timestamp: Optional[datetime] = Field(
        default=None,
        description="ISO-8601 UTC login time. Defaults to server time.",
    )
    geo_velocity_kmh: float = Field(
        default=0.0,
        ge=0.0,
        description="Implied travel speed since previous login (km/h).",
    )
    is_new_device: bool = Field(default=False)
    is_new_country: bool = Field(default=False)
    failed_attempts: int = Field(default=0, ge=0)
    session_duration_s: int = Field(default=0, ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "alice",
                    "timestamp": "2026-11-03T03:14:00Z",
                    "geo_velocity_kmh": 980,
                    "is_new_device": True,
                    "is_new_country": True,
                    "failed_attempts": 4,
                    "session_duration_s": 12,
                }
            ]
        }
    }


class LoginResponse(BaseModel):
    """Risk assessment + explanation for a login event."""

    user_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    is_anomaly: bool
    explanation: str
    suggested_action: str
    feature_contributions: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    version: str