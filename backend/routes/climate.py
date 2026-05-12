"""
backend/routes/climate.py
GET /api/v1/climate-alerts  —  push local forecast to devices.
Devices cache this and use it to adjust triage prompts offline.
Apache 2.0 — see LICENSE
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["climate"])


@router.get("/climate-alerts")
async def get_climate_alerts(region: str = "paderu_araku"):
    """
    In production: pulls from India Meteorological Department API,
    NASA POWER API (heat index), and district DHIS2 surveillance.
    Stub returns a representative monsoon-season response.
    """
    return {
        "region":       region,
        "generated_at": datetime.utcnow().isoformat(),
        "alerts": [
            {
                "hazard":        "MONSOON_ACTIVE",
                "severity":      "HIGH",
                "message":       "Monsoon week 4. Malaria and diarrhoeal disease risk elevated.",
                "diseases":      ["Malaria", "Diarrhoeal disease"],
                "chw_action":    "Suspect malaria for any fever. Ensure ORS stocks.",
                "expires_hours": 72,
            }
        ],
        "forecast_72h": {
            "temperature_c": 28,
            "humidity_pct":  84,
            "rainfall_mm":   45,
            "heat_index_c":  33,
        },
    }
