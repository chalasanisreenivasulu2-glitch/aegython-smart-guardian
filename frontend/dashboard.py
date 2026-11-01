"""
frontend/dashboard.py
Streamlit UI for Smart Login Guardian — talks to FastAPI on :8000.
"""
from __future__ import annotations

import os
from datetime import datetime

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

PRESETS: dict[str, dict] = {
    "✅ Normal login": {
        "user_id": "alice",
        "timestamp": "2026-11-04T11:45:00Z",
        "geo_velocity_kmh": 15.0,
        "is_new_device": False,
        "is_new_country": False,
        "failed_attempts": 0,
        "session_duration_s": 1800,
    },
    "🌍 Impossible travel": {
        "user_id": "alice",
        "timestamp": "2026-11-03T03:14:00Z",
        "geo_velocity_kmh": 980.0,
        "is_new_device": True,
        "is_new_country": True,
        "failed_attempts": 4,
        "session_duration_s": 12,
    },
    "🌙 Weekend off-hours": {
        "user_id": "bob",
        "timestamp": "2026-11-07T02:00:00Z",
        "geo_velocity_kmh": 30.0,
        "is_new_device": True,
        "is_new_country": False,
        "failed_attempts": 2,
        "session_duration_s": 45,
    },
}

ACTION_EMOJI = {
    "ALLOW": "🟢",
    "CHALLENGE_MFA": "🟡",
    "BLOCK_AND_CHALLENGE_MFA": "🔴",
}

st.set_page_config(page_title="Smart Login Guardian", page_icon="🛡️", layout="wide")

st.title("🛡️ Smart Login Guardian")
st.caption("Explainable login anomaly detection — AEGYTHON 2026")

try:
    health = requests.get(f"{API_URL}/health", timeout=2)
    backend_ok = health.status_code == 200
    backend_version = health.json().get("version", "?") if backend_ok else None
except requests.RequestException:
    backend_ok = False
    backend_version = None

if backend_ok:
    st.success(f"Backend online at {API_URL} (v{backend_version})")
else:
    st.error(
        f"Backend unreachable at {API_URL}. Start it with:\n\n"
        "`uvicorn app.main:app --reload --port 8000`"
    )
    st.stop()

st.subheader("1. Load a demo scenario (or edit the fields below)")
cols = st.columns(len(PRESETS))
for col, (label, payload) in zip(cols, PRESETS.items()):
    if col.button(label, use_container_width=True):
        st.session_state["payload"] = payload.copy()
        st.rerun()

if "payload" not in st.session_state:
    st.session_state["payload"] = PRESETS["✅ Normal login"].copy()

p = st.session_state["payload"]

st.subheader("2. Login event")
with st.form("login_form"):
    c1, c2, c3 = st.columns(3)
    user_id = c1.text_input("User ID", p["user_id"])
    ts_str = c2.text_input("Timestamp (ISO-8601 UTC)", p["timestamp"])
    geo_velocity = c3.number_input(
        "Geo velocity (km/h)", min_value=0.0, max_value=2000.0,
        value=float(p["geo_velocity_kmh"]), step=10.0,
    )

    c4, c5, c6 = st.columns(3)
    is_new_device = c4.checkbox("New device", value=p["is_new_device"])
    is_new_country = c5.checkbox("New country", value=p["is_new_country"])
    failed_attempts = c6.number_input(
        "Failed attempts", min_value=0, max_value=20,
        value=int(p["failed_attempts"]), step=1,
    )

    session_duration = st.number_input(
        "Session duration (s)", min_value=0, max_value=86400,
        value=int(p["session_duration_s"]), step=30,
    )

    submitted = st.form_submit_button("🔍 Analyze", use_container_width=True)

if submitted:
    try:
        datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError as exc:
        st.error(f"Invalid timestamp: {exc}")
        st.stop()

    body = {
        "user_id": user_id,
        "timestamp": ts_str,
        "geo_velocity_kmh": geo_velocity,
        "is_new_device": is_new_device,
        "is_new_country": is_new_country,
        "failed_attempts": failed_attempts,
        "session_duration_s": session_duration,
    }

    try:
        resp = requests.post(f"{API_URL}/analyze_login", json=body, timeout=5)
        resp.raise_for_status()
        result = resp.json()
    except requests.HTTPError:
        st.error(f"API error {resp.status_code}: {resp.text}")
        st.stop()
    except requests.RequestException as exc:
        st.error(f"Network error: {exc}")
        st.stop()

    st.session_state["payload"] = {**body, "timestamp": ts_str}

    st.subheader("3. Verdict")
    v1, v2, v3 = st.columns(3)
    v1.metric("Risk score", f"{result['risk_score']:.3f}")
    v2.metric("Anomaly", "YES" if result["is_anomaly"] else "no")
    v3.metric(
        "Suggested action",
        f"{ACTION_EMOJI.get(result['suggested_action'], '')} {result['suggested_action']}",
    )

    if result["is_anomaly"]:
        st.error(f"🚨 **{result['explanation']}**")
    else:
        st.success(f"✅ {result['explanation']}")

    st.subheader("4. Why? — feature contributions")
    st.caption(
        "Normalised |z-score| against the baseline. Higher = the feature drove "
        "this classification more."
    )
    contrib = result["feature_contributions"]
    sorted_contrib = dict(sorted(contrib.items(), key=lambda kv: kv[1], reverse=True))
    st.bar_chart(sorted_contrib, height=320)

    with st.expander("Raw response"):
        st.json(result)

st.divider()
st.caption(
    "Smart Login Guardian · AEGYTHON 2026 · "
    "All traffic is synthetic and sent to localhost only."
)