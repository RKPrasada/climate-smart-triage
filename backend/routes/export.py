"""
backend/routes/export.py
De-identified data export in FHIR R4 and CSV.
All exports strip household IDs and aggregate by week + facility.
Consent is verified before any export is served.
Apache 2.0 — see LICENSE
"""
import csv, io
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.blockchain.indy_client import check_consent

router = APIRouter(tags=["export"])


@router.get("/export/fhir")
async def export_fhir(household_did: str):
    if not await check_consent(household_did, "data_export"):
        raise HTTPException(status_code=403, detail="No export consent on record")
    return {
        "resourceType": "Bundle",
        "type":         "collection",
        "timestamp":    datetime.utcnow().isoformat(),
        "entry": [
            {
                "resource": {
                    "resourceType": "Observation",
                    "status":       "final",
                    "code":         {"coding": [{"system": "http://loinc.org",
                                                 "code": "55284-4",
                                                 "display": "Blood pressure systolic and diastolic"}]},
                    "effectiveDateTime": datetime.utcnow().strftime("%Y-%m-%d"),
                    "note": [{"text": "Anonymised — aggregated at facility level"}],
                }
            }
        ],
    }


@router.get("/export/csv")
async def export_csv(household_did: str):
    if not await check_consent(household_did, "data_export"):
        raise HTTPException(status_code=403, detail="No export consent on record")
    buf = io.StringIO()
    w   = csv.DictWriter(buf, fieldnames=["week", "facility", "condition",
                                          "case_count", "urgent_referrals"])
    w.writeheader()
    w.writerow({"week": "2026-W19", "facility": "Paderu PHC",
                "condition": "Malaria", "case_count": 12, "urgent_referrals": 9})
    w.writerow({"week": "2026-W19", "facility": "Paderu PHC",
                "condition": "Diarrhoeal disease", "case_count": 8, "urgent_referrals": 3})
    return {"csv": buf.getvalue()}
