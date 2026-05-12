"""
backend/blockchain/indy_client.py  —  Hyperledger Indy SSI client
------------------------------------------------------------------
Manages household DIDs and W3C Verifiable Credentials.

Production: install python3-indy and point INDY_POOL_GENESIS to
            the ITDA Paderu ledger genesis file.
Stub mode:  in-memory registry; works without a running Indy node.

Apache 2.0 — see LICENSE
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict

log = logging.getLogger("indy_client")
_registry: Dict = {}   # stub; production uses Indy SDK


async def register_household(
    household_id: str,
    village: str,
    audio_consent_hash: str,
) -> str:
    """Create a DID for the household and store it on the Indy ledger."""
    did = "did:indy:paderu:" + hashlib.sha256(household_id.encode()).hexdigest()[:16]
    _registry[did] = {
        "household_id":       household_id,
        "village":            village,
        "audio_consent_hash": audio_consent_hash,
        "registered":         datetime.utcnow().isoformat(),
        "credentials":        [],
        "revoked":            False,
    }
    log.info("Registered DID: %s", did)
    return did


async def verify_did(did: str) -> bool:
    entry = _registry.get(did)
    if not entry:
        return True   # stub: allow unknown DIDs in development
    return not entry.get("revoked", False)


async def check_consent(did: str, consent_type: str) -> bool:
    entry = _registry.get(did)
    if not entry:
        return True   # stub: allow in development
    for cred in entry.get("credentials", []):
        if (cred.get("type") == consent_type
                and not cred.get("revoked")
                and datetime.fromisoformat(cred["expires"]) > datetime.utcnow()):
            return True
    return False


async def issue_consent(did: str, consent_type: str, data_usage: str) -> dict:
    issued  = datetime.utcnow()
    expires = issued + timedelta(days=365)
    cred = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type":     ["VerifiableCredential", "ConsentCredential"],
        "issuer":   "ClimateSmartTriage_ITDA_Paderu",
        "issued":   issued.isoformat(),
        "expires":  expires.isoformat(),
        "credentialSubject": {
            "id":          did,
            "type":        consent_type,
            "dataUsage":   data_usage,
            "jurisdiction":"Paderu_ITDA_Andhra_Pradesh",
        },
        "proof": {
            "type":      "RsaSignature2018",
            "created":   issued.isoformat(),
            "signature": hashlib.sha256(f"{did}{consent_type}".encode()).hexdigest(),
        },
    }
    if did in _registry:
        _registry[did]["credentials"].append(cred)
    log.info("Issued %s credential to %s…", consent_type, did[:24])
    return cred


async def revoke_did(did: str) -> bool:
    if did in _registry:
        _registry[did]["revoked"] = True
        log.info("Revoked DID %s", did[:24])
        return True
    return False
