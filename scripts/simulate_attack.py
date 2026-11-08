"""
scripts/simulate_attack.py
Fire a batch of synthetic login events at the running API and print a summary.

Usage (from project root, venv active):
    python -m scripts.simulate_attack
    python -m scripts.simulate_attack --url http://127.0.0.1:8000 --runs 20

All traffic is synthetic and sent to localhost only — no external systems.
"""
from __future__ import annotations

import argparse
import random
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

import requests

# ---------------------------------------------------------------------------
# Scenario generators — one event each, matching the validated archetypes.
# ---------------------------------------------------------------------------
def normal_login(i: int) -> dict:
    return {
        "user_id": f"alice{i % 5}",
        "timestamp": (datetime(2026, 11, 4, 11, 45, tzinfo=timezone.utc)
                      + timedelta(minutes=i)).isoformat(),
        "geo_velocity_kmh": round(random.uniform(5, 40), 1),
        "is_new_device": False,
        "is_new_country": False,
        "failed_attempts": 0,
        "session_duration_s": random.randint(900, 3600),
    }


def impossible_travel(i: int) -> dict:
    return {
        "user_id": f"alice{i % 5}",
        "timestamp": (datetime(2026, 11, 3, 3, 14, tzinfo=timezone.utc)
                      + timedelta(minutes=i)).isoformat(),
        "geo_velocity_kmh": round(random.uniform(800, 1400), 1),
        "is_new_device": True,
        "is_new_country": True,
        "failed_attempts": random.randint(2, 6),
        "session_duration_s": random.randint(5, 60),
    }


def weekend_offhours(i: int) -> dict:
    return {
        "user_id": f"bob{i % 3}",
        "timestamp": (datetime(2026, 11, 7, 2, 0, tzinfo=timezone.utc)
                      + timedelta(minutes=i)).isoformat(),
        "geo_velocity_kmh": round(random.uniform(10, 60), 1),
        "is_new_device": True,
        "is_new_country": False,
        "failed_attempts": random.randint(1, 4),
        "session_duration_s": random.randint(20, 90),
    }


GENERATORS = {
    "normal": normal_login,
    "impossible_travel": impossible_travel,
    "weekend_offhours": weekend_offhours,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Fire synthetic logins at Smart Login Guardian.")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--runs", type=int, default=9,
                        help="Events per archetype (default 9 → 27 total).")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    # Health check first — clean error if the API isn't up.
    try:
        h = requests.get(f"{args.url}/health", timeout=3)
        h.raise_for_status()
    except requests.RequestException as exc:
        print(f"[error] API not reachable at {args.url}: {exc}", file=sys.stderr)
        print("        Start it with: uvicorn app.main:app --port 8000", file=sys.stderr)
        return 1

    print(f"[ok] API healthy at {args.url}")
    print(f"[run] {args.runs} events per archetype, seed={args.seed}\n")

    results = []
    for name, gen in GENERATORS.items():
        for i in range(args.runs):
            payload = gen(i)
            r = requests.post(f"{args.url}/analyze_login", json=payload, timeout=5)
            r.raise_for_status()
            body = r.json()
            results.append({
                "archetype": name,
                "user_id": body["user_id"],
                "risk_score": body["risk_score"],
                "is_anomaly": body["is_anomaly"],
                "action": body["suggested_action"],
                "top_feature": max(body["feature_contributions"].items(),
                                   key=lambda kv: kv[1])[0],
            })

    # Summary
    print(f"{'archetype':<20} {'runs':>4} {'anomalies':>9} {'mean_risk':>9} {'top_feature':<20}")
    print("-" * 68)
    for name in GENERATORS:
        rows = [x for x in results if x["archetype"] == name]
        n_anom = sum(1 for x in rows if x["is_anomaly"])
        mean_risk = sum(x["risk_score"] for x in rows) / len(rows)
        top = Counter(x["top_feature"] for x in rows).most_common(1)[0][0]
        print(f"{name:<20} {len(rows):>4} {n_anom:>9} {mean_risk:>9.3f} {top:<20}")

    # Assertions — the "this is a test, not a demo" part
    by_arch = {name: [x for x in results if x["archetype"] == name] for name in GENERATORS}
    assert all(not x["is_anomaly"] for x in by_arch["normal"]), \
        "normal events must not be flagged as anomalies"
    assert all(x["is_anomaly"] for x in by_arch["impossible_travel"]), \
        "impossible travel must always be flagged"
    assert all(x["is_anomaly"] for x in by_arch["weekend_offhours"]), \
        "weekend off-hours must always be flagged"

    print("\n[ok] all archetype invariants held")
    return 0


if __name__ == "__main__":
    sys.exit(main())