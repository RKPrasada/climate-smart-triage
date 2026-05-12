"""
backend/routes/consent.py
Household registration and consent credential issuance.
Apache 2.0 — see LICENSE
"""
from fastapi import APIRouter
from pydantic import BaseModel
from backend.blockchain.indy_client import register_household, issue_consent
import logging

log    = logging.getLogger("routes.consent")
router = APIRouter(tags=["consent"])


class RegistrationRequest(BaseModel):
    household_id:        str
    village:             str
    audio_consent_hash:  str   # SHA-256 of the Telugu audio consent recording


class ConsentRequest(BaseModel):
    household_did: str
    consent_type:  str   # health_data_collection | ai_triage_use | federated_learning
    data_usage:    str


@router.post("/consent/register")
async def register(req: RegistrationRequest):
    did = await register_household(req.household_id, req.village, req.audio_consent_hash)
    log.info("Registered %s → %s…", req.household_id, did[:24])
    return {"did": did, "status": "registered"}


@router.post("/consent/issue")
async def issue(req: ConsentRequest):
    credential = await issue_consent(req.household_did, req.consent_type, req.data_usage)
    return {"credential": credential, "status": "issued"}
