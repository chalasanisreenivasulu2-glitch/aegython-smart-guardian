"""
app/ml/data_generator.py
Synthetic baseline + attack login generator for Smart Login Guardian.

Used in two ways:
  1. Imported by detector.py to build the training set for the Isolation Forest.
  2. Run as a CLI to dump CSVs for the demo video / Streamlit dashboard.

    python -m app.ml.data_generator --out data/
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Single source of truth for column order — imported by detector.py
FEATURES = [
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "geo_velocity_kmh",
    "is_new_device",
    "is_new_country",
    "failed_attempts",
    "session_duration_s",
]


# ---------------------------------------------------------------------------
# Normal (legit) login behaviour
# ---------------------------------------------------------------------------
def generate_baseline(n_samples: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Realistic *normal* office-worker login pattern, now including
    ~10% legitimate weekend logins so `is_weekend` carries signal.
    """
    rng = np.random.default_rng(seed)

    is_weekend = rng.binomial(1, 0.10, size=n_samples)

    # Weekdays: Mon-Fri (0-4), 08:00-19:00 centred at 12:00
    # Weekends: Sat-Sun (5-6), 10:00-21:00 centred at 14:00
    dow_weekday = rng.integers(0, 5, size=n_samples)
    dow_weekend = rng.integers(5, 7, size=n_samples)
    dow = np.where(is_weekend, dow_weekend, dow_weekday)

    hour_weekday = rng.normal(12, 2.5, size=n_samples).clip(7, 20)
    hour_weekend = rng.normal(14, 3.0, size=n_samples).clip(9, 22)
    hour = np.where(is_weekend, hour_weekend, hour_weekday).astype(int)

    geo_vel = rng.normal(20, 15, size=n_samples).clip(0, 120)
    new_device = rng.binomial(1, 0.03, size=n_samples)
    new_country = rng.binomial(1, 0.01, size=n_samples)
    failed = rng.poisson(0.2, size=n_samples).clip(0, 3)
    session = rng.normal(1800, 600, size=n_samples).clip(60, 7200)

    return pd.DataFrame({
        "hour_of_day": hour,
        "day_of_week": dow,
        "is_weekend": is_weekend,
        "geo_velocity_kmh": geo_vel,
        "is_new_device": new_device,
        "is_new_country": new_country,
        "failed_attempts": failed,
        "session_duration_s": session,
    })[FEATURES]
# ---------------------------------------------------------------------------
# Attack / anomalous login behaviour (for demos + negative-sample sanity check)
# ---------------------------------------------------------------------------
def generate_attacks(n_samples: int = 200, seed: int = 7) -> pd.DataFrame:
    """
    Three attack archetypes blended together:
      - impossible travel   (huge geo_velocity)
      - credential stuffing (many failed attempts, new country)
      - off-hours bot       (3am login, near-zero session)
    """
    rng = np.random.default_rng(seed)
    per = n_samples // 3

    # --- impossible travel ---
    it = pd.DataFrame({
        "hour_of_day": rng.integers(0, 24, per),
        "day_of_week": rng.integers(0, 7, per),
        "is_weekend": rng.integers(0, 2, per),
        "geo_velocity_kmh": rng.uniform(800, 1500, per),
        "is_new_device": rng.integers(0, 2, per),
        "is_new_country": np.ones(per, dtype=int),
        "failed_attempts": rng.integers(0, 2, per),
        "session_duration_s": rng.integers(30, 300, per),
    })

    # --- credential stuffing ---
    cs = pd.DataFrame({
        "hour_of_day": rng.integers(0, 24, per),
        "day_of_week": rng.integers(0, 7, per),
        "is_weekend": rng.integers(0, 2, per),
        "geo_velocity_kmh": rng.uniform(200, 800, per),
        "is_new_device": np.ones(per, dtype=int),
        "is_new_country": np.ones(per, dtype=int),
        "failed_attempts": rng.integers(3, 10, per),
        "session_duration_s": rng.integers(1, 30, per),
    })

    # --- off-hours bot ---
    ob = pd.DataFrame({
        "hour_of_day": rng.integers(1, 5, per),          # 01:00-04:59
        "day_of_week": rng.integers(0, 7, per),
        "is_weekend": rng.integers(0, 2, per),
        "geo_velocity_kmh": rng.uniform(0, 100, per),
        "is_new_device": rng.integers(0, 2, per),
        "is_new_country": rng.integers(0, 2, per),
        "failed_attempts": rng.integers(0, 3, per),
        "session_duration_s": rng.integers(1, 60, per),
    })

    return pd.concat([it, cs, ob], ignore_index=True)[FEATURES]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic login data.")
    parser.add_argument("--out", default="data", help="Output directory for CSVs")
    parser.add_argument("--normal", type=int, default=2000)
    parser.add_argument("--attacks", type=int, default=200)
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    baseline = generate_baseline(args.normal)
    attacks = generate_attacks(args.attacks)

    baseline.to_csv(out / "baseline.csv", index=False)
    attacks.to_csv(out / "attacks.csv", index=False)

    print(f"[ok] baseline : {len(baseline):>5} rows -> {out/'baseline.csv'}")
    print(f"[ok] attacks  : {len(attacks):>5} rows -> {out/'attacks.csv'}")
    print(f"[ok] columns  : {FEATURES}")


if __name__ == "__main__":
    _main()