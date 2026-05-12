"""
backend/routes/federated.py
POST /api/v1/federated-gradient  —  receive model gradient from device.

Devices NEVER send raw patient data.
They compute a local gradient and send only that.
The server aggregates gradients from 50+ devices to improve the global model.

Apache 2.0 — see LICENSE
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.blockchain.indy_client import check_consent
from backend.blockchain.besu_audit  import log_access
from backend.federated.aggregator   import queue_gradient
import logging

log    = logging.getLogger("routes.federated")
router = APIRouter(tags=["federated"])


class GradientPayload(BaseModel):
    household_did:   str
    model_version:   str
    gradient_hash:   str   # SHA-256 integrity check
    gradient_values: dict


@router.post("/federated-gradient")
async def receive_gradient(payload: GradientPayload):
    if not await check_consent(payload.household_did, "federated_learning"):
        raise HTTPException(status_code=403,
                            detail="Household has not consented to federated learning")

    await queue_gradient(payload.household_did, payload.gradient_values)

    await log_access(
        did         = payload.household_did,
        access_type = "federated_gradient",
        purpose     = "Model improvement — no raw data shared",
    )

    log.info("Gradient queued from %s…", payload.household_did[:24])
    return {"status": "gradient_received"}
