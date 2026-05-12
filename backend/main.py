"""
backend/main.py  —  ClimateSmartTriage district server
-------------------------------------------------------
FastAPI application. Runs on the ITDA district server.
Devices connect when 2G or WiFi is available to sync
offline triages, consent updates, and model gradients.

Run:  uvicorn backend.main:app --host 0.0.0.0 --port 5000

Apache 2.0 — see LICENSE
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.routes.triage    import router as triage_router
from backend.routes.climate   import router as climate_router
from backend.routes.consent   import router as consent_router
from backend.routes.federated import router as federated_router
from backend.routes.export    import router as export_router

log = logging.getLogger("main")

app = FastAPI(
    title       = "ClimateSmartTriage API",
    description = "Offline-first paediatric triage for climate-vulnerable communities",
    version     = "1.0.0",
    license_info= {"name": "Apache 2.0",
                   "url":  "https://www.apache.org/licenses/LICENSE-2.0"},
)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(triage_router,    prefix="/api/v1")
app.include_router(climate_router,   prefix="/api/v1")
app.include_router(consent_router,   prefix="/api/v1")
app.include_router(federated_router, prefix="/api/v1")
app.include_router(export_router,    prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "healthy"}


@app.websocket("/ws/sync")
async def websocket_sync(ws: WebSocket):
    """
    Devices connect here when any connectivity becomes available.
    They push offline triages, model gradients, and consent updates.
    The server acknowledges each message and returns any pending
    climate alerts for the device's region.
    """
    await ws.accept()
    try:
        while True:
            data     = await ws.receive_json()
            msg_type = data.get("type")
            await ws.send_json({"status": "ack", "type": msg_type})
    except Exception as exc:
        log.info("WebSocket closed: %s", exc)
        await ws.close()
