"""
app/explainer/generator.py
Rule-based explainer — swaps cleanly for an LLM later.
"""
from __future__ import annotations

# Human-readable phrases keyed by feature name
_FEATURE_PHRASES = {
    "hour_of_day": "unusual login time",
    "day_of_week": "unusual day of week",
    "is_weekend": "weekend activity",
    "geo_velocity_kmh": "impossible travel",
    "is_new_device": "unrecognised device",
    "is_new_country": "new country",
    "failed_attempts": "multiple failed attempts",
    "session_duration_s": "abnormal session length",
}


def explain(risk_score: float, contributions: dict[str, float]) -> str:
    """Build a one-sentence explanation from the top contributing features."""
    if risk_score < 0.3:
        return "Login looks normal — no significant anomalies detected."

    top = sorted(contributions.items(), key=lambda kv: kv[1], reverse=True)[:3]
    reasons = [_FEATURE_PHRASES.get(f, f) for f, _ in top]
    joined = ", ".join(reasons[:-1]) + (f" and {reasons[-1]}" if len(reasons) > 1 else reasons[0])
    return f"High risk (score {risk_score:.2f}): {joined}."


def suggested_action(risk_score: float) -> str:
    """Map risk score to a recommended SOC action."""
    if risk_score >= 0.7:
        return "BLOCK_AND_CHALLENGE_MFA"
    if risk_score >= 0.4:
        return "CHALLENGE_MFA"
    return "ALLOW"