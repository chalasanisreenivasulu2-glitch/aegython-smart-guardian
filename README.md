# Smart Login Guardian — AEGYTHON 2026

> **Challenge 1:** Build a tool that detects suspicious synthetic login attempts and explains the risk signals behind its decisions.

Smart Login Guardian is an explainable AI security tool that scores login events for risk and provides human-readable explanations for its decisions.

## Setup Instructions

### Option A: Docker (Recommended)

```bash
git clone https://github.com/chalasanisreenivasulu2-glitch/aegython-smart-guardian.git
cd aegython-smart-guardian
docker compose up --build
```
- API Docs: `http://localhost:8000/docs`
- Streamlit UI: `http://localhost:8501`

### Option B: Local Execution

```powershell
python -m venv venv
\.\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

# Terminal 1: Backend
uvicorn app.main:app --port 8000

# Terminal 2: Frontend
streamlit run frontend/dashboard.py
```

## Explanation of the Intelligent Technique

We use **Unsupervised Anomaly Detection (Isolation Forest)**. Instead of relying on hardcoded thresholds, the model learns the distribution of "normal" behavior across 8 dimensions (hour of day, day of week, geo-velocity, device status, etc.). To satisfy the "explainable" requirement, we calculate the absolute z-score of each feature against the baseline distribution, normalizing them to sum to 1.0. This provides a SHAP-like explainability without the heavy computational overhead, showing exactly why the model made its decision.

## Test Evidence

The project includes a full pytest suite covering the ML logic and API endpoints. To reproduce:

```bash
pytest -v

```
Expected output: `8 passed in ~2.5s`. Test files are located in `tests/`.

## Attribution and Known Limitations

**Attribution:** Built from scratch during the AEGYTHON 2026 hackathon. Synthetic data generated using numpy and pandas. Machine learning powered by scikit-learn. Backend: FastAPI, UI: Streamlit.

**Known Limitations:** The baseline for the Isolation Forest is generated on-the-fly at startup using a fixed seed, ensuring immediate reproducibility but not trained on real historical data. The explainer module uses a rule-based mapping of normalized z-scores to natural language. The API handles single-event scoring.
