"""
Machine-learning layer for Smart Login Guardian.

Import the detector explicitly:
    from app.ml.detector import score_login, train_model
or use the convenience re-export:
    from app.ml import score_login
The re-export is lazy (PEP 562) so `python -m app.ml.detector` runs cleanly.
"""
from app.ml.data_generator import FEATURES, generate_attacks, generate_baseline

__all__ = [
    "FEATURES",
    "generate_attacks",
    "generate_baseline",
    "score_login",
    "train_model",
]


def __getattr__(name):
    """Lazy re-export — avoids importing detector at package-init time."""
    if name in {"score_login", "train_model"}:
        from app.ml import detector
        return getattr(detector, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")