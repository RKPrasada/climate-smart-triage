"""
backend/federated/aggregator.py  —  Federated learning aggregation
-------------------------------------------------------------------
Devices send only model gradients — never raw patient data.
This module averages gradients from many devices and applies
the combined update to the global model.

Production: runs as a Celery task; writes proof-of-contribution
            to the Besu AuditLog smart contract.
Stub mode:  in-memory queue; identical interface.

Apache 2.0 — see LICENSE
"""
import logging
from typing import Dict

log      = logging.getLogger("aggregator")
_pending: list = []


async def queue_gradient(household_did: str, gradient: Dict) -> None:
    _pending.append({"did": household_did, "gradient": gradient})
    log.info("Gradient queued — queue size: %d", len(_pending))
    if len(_pending) >= 10:
        await aggregate()


async def aggregate() -> Dict:
    if not _pending:
        return {}
    log.info("Aggregating %d gradients …", len(_pending))

    merged: Dict = {}
    for item in _pending:
        for param, values in item["gradient"].items():
            if param not in merged:
                merged[param] = []
            if isinstance(values, list):
                merged[param].extend(values)

    averaged = {k: sum(v) / len(v) for k, v in merged.items() if v}
    _pending.clear()
    log.info("Aggregation complete — %d parameters updated", len(averaged))
    return averaged
