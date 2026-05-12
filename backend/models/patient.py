"""
backend/models/patient.py  —  Pydantic request/response schemas
Apache 2.0 — see LICENSE
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class PatientVitals(BaseModel):
    age_months:       int           = Field(..., ge=0, le=60)
    weight_kg:        float         = Field(..., gt=0)
    temperature_c:    float
    respiratory_rate: Optional[int] = None
    heart_rate:       Optional[int] = None
    chief_complaint:  str
    symptoms:         List[str]     = []

    model_config = {
        "json_schema_extra": {"example": {
            "age_months": 18, "weight_kg": 8.5, "temperature_c": 39.2,
            "respiratory_rate": 58, "heart_rate": 135,
            "chief_complaint": "fever and loose stools",
            "symptoms": ["fever", "diarrhea", "lethargy"],
        }}
    }


class ClimateContext(BaseModel):
    temperature_c:  Optional[float] = None
    humidity_pct:   Optional[float] = None
    recent_event:   Optional[str]   = None
    disease_alert:  Optional[str]   = None
    water_quality:  Optional[str]   = None


class TriageRequest(BaseModel):
    household_did:   str
    patient_vitals:  PatientVitals
    climate_context: ClimateContext = ClimateContext()


class TriageResponse(BaseModel):
    urgency:            str
    triage_output:      str
    recommended_action: str
    model:              str
