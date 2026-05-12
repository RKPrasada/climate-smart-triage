"""
backend/tests/test_triage_route.py
Smoke tests for the triage API.
Run: pytest backend/tests/
Apache 2.0 — see LICENSE
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

MOCK_RESPONSE = "URGENT REFERRAL\nDanger signs present.\nAction: refer to health facility now."

with patch("model.inference.triage_engine.run_inference", new=AsyncMock(return_value=MOCK_RESPONSE)):
    from backend.main import app

client = TestClient(app)

SAMPLE = {
    "household_did": "did:indy:paderu:testdid001",
    "patient_vitals": {
        "age_months": 18, "weight_kg": 8.5, "temperature_c": 39.2,
        "respiratory_rate": 58, "heart_rate": 135,
        "chief_complaint": "fever and loose stools",
        "symptoms": ["fever", "diarrhea", "lethargy"],
    },
    "climate_context": {
        "temperature_c": 28, "humidity_pct": 85,
        "recent_event": "heavy rainfall", "disease_alert": "malaria season",
    },
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_triage_returns_urgency():
    r = client.post("/api/v1/triage", json=SAMPLE)
    assert r.status_code == 200
    assert r.json()["urgency"] in ("RED", "YELLOW", "GREEN")


def test_triage_returns_action():
    r = client.post("/api/v1/triage", json=SAMPLE)
    assert "recommended_action" in r.json()
    assert len(r.json()["recommended_action"]) > 5


def test_climate_alerts():
    r = client.get("/api/v1/climate-alerts")
    assert r.status_code == 200
    assert "alerts" in r.json()
    assert len(r.json()["alerts"]) > 0
