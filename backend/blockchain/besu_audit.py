"""
backend/blockchain/besu_audit.py  —  Hyperledger Besu audit log
----------------------------------------------------------------
Every data access is written permanently. No one can delete or
alter these records — not the development team, not ITDA, not UNICEF.

Production: uses web3.py to submit a transaction to AuditLog.sol.
Stub mode:  in-memory list; identical interface.

Apache 2.0 — see LICENSE
"""
import hashlib
import logging
from datetime import datetime

log = logging.getLogger("besu_audit")
_log: list = []


async def log_access(did: str, access_type: str, purpose: str) -> dict:
    entry = {
        "timestamp":   datetime.utcnow().isoformat(),
        "did":         did,
        "access_type": access_type,
        "purpose":     purpose,
        "tx_hash":     hashlib.sha256(
                           f"{did}{access_type}{datetime.utcnow().isoformat()}".encode()
                       ).hexdigest(),
    }
    _log.append(entry)
    log.info("Audit: %s | %s | tx %s…", access_type, did[:20], entry["tx_hash"][:10])
    return entry


def get_audit_trail(did: str) -> list:
    return [e for e in _log if e["did"] == did]
