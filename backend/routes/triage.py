"""
backend/routes/triage.py
POST /api/v1/triage  —  receive device triage, run AI, write audit log.
Apache 2.0 — see LICENSE
"""
from fastapi import APIRouter, HTTPException
from backend.models.patient import TriageRequest, TriageResponse
from backend.blockchain.indy_client import verify_did
from backend.blockchain.besu_audit  import log_access
from model.inference.triage_engine  import triage
import logging

log    = logging.getLogger("routes.triage")
router = APIRouter(tags=["triage"])


@router.post("/triage", response_model=TriageResponse)
async def run_triage(request: TriageRequest):
    """
    1. Verify household DID on Hyperledger Indy ledger.
    2. Run climate-aware AI triage via local Ollama model.
    3. Write immutable access record to Hyperledger Besu.
    4. Return triage result.
    """
    if not await verify_did(request.household_did):
        raise HTTPException(status_code=401, detail="Unrecognised household DID")

    result = await triage(
        vitals  = request.patient_vitals.model_dump(),
        climate = request.climate_context.model_dump(),
    )

    await log_access(
        did         = request.household_did,
        access_type = "triage_inference",
        purpose     = "Paediatric climate-health assessment",
    )

    log.info("Triage complete — urgency %s — DID %s…",
             result["urgency"], request.household_did[:24])
    return TriageResponse(**result)
