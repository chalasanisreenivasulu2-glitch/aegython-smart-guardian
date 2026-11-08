"""
scripts/record_demo.py
Interactive demo script for AEGYTHON 2026.
Run this while your FastAPI server is active on port 8000.
"""
import requests
import json
import time
import sys

API_URL = "http://127.0.0.1:8000/analyze_login"
HEALTH_URL = "http://127.0.0.1:8000/health"

def check_health():
    try:
        r = requests.get(HEALTH_URL, timeout=2)
        if r.status_code == 200:
            print("🟢 API is UP and running.\n")
            return True
    except requests.ConnectionError:
        print("🔴 API is DOWN. Please start it first:")
        print("   uvicorn app.main:app --port 8000\n")
        return False
    return False

def print_separator(title):
    print("\n" + "="*60)
    print(f"🔹 {title}")
    print("="*60)

def run_scenario(name, payload):
    print_separator(f"SCENARIO: {name}")
    print(f"📥 INPUT PAYLOAD:\n{json.dumps(payload, indent=2)}\n")
    
    print("⏳ Sending request to API...")
    time.sleep(1) # dramatic pause
    
    try:
        r = requests.post(API_URL, json=payload)
        r.raise_for_status()
        res = r.json()
        
        print(f"📤 RISK SCORE: {res['risk_score']}")
        print(f"🚨 IS ANOMALY: {res['is_anomaly']}")
        print(f"🛡️  ACTION:     {res['suggested_action']}")
        print(f"💡 EXPLANATION: {res['explanation']}\n")
        
        print("📊 TOP FEATURE CONTRIBUTIONS:")
        # Sort contributions and show top 3
        sorted_feats = sorted(res['feature_contributions'].items(), key=lambda x: x[1], reverse=True)
        for feat, score in sorted_feats[:3]:
            bar = "█" * int(score * 50)
            print(f"   {feat:<20} | {score:.3f} {bar}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if not check_health():
        sys.exit(1)

    # Scenario 1: Normal
    run_scenario("Normal Login", {
        "user_id": "alice",
        "timestamp": "2026-11-04T11:45:00Z",
        "geo_velocity_kmh": 15.0,
        "is_new_device": False,
        "is_new_country": False,
        "failed_attempts": 0,
        "session_duration_s": 1800
    })
    time.sleep(2)

    # Scenario 2: Impossible Travel
    run_scenario("Impossible Travel (Attack)", {
        "user_id": "alice",
        "timestamp": "2026-11-03T03:14:00Z",
        "geo_velocity_kmh": 980.0,
        "is_new_device": True,
        "is_new_country": True,
        "failed_attempts": 4,
        "session_duration_s": 12
    })
    time.sleep(2)

    # Scenario 3: Weekend Off-Hours
    run_scenario("Weekend Off-Hours (Attack)", {
        "user_id": "bob",
        "timestamp": "2026-11-07T02:00:00Z",
        "geo_velocity_kmh": 30.0,
        "is_new_device": True,
        "is_new_country": False,
        "failed_attempts": 2,
        "session_duration_s": 45
    })
    
    print("\n✅ Demo complete.")