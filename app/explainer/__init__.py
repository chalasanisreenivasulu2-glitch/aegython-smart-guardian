"""
Explainability layer for Smart Login Guardian.

Turns the detector's numeric output (risk_score + feature_contributions)
into a human-readable sentence and a suggested action.
"""
from app.explainer.generator import explain, suggested_action

__all__ = ["explain", "suggested_action"]