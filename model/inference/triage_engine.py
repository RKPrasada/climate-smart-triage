"""
model/inference/triage_engine.py  —  ClimateSmartTriage
---------------------------------------------------------
Wraps the Ollama local inference daemon and builds climate-aware
triage prompts. Called by the FastAPI backend and by the Flutter
app's local method channel when connectivity is unavailable.

Apache 2.0 — see LICENSE
"""

import logging
import re
from typing import Dict, Optional

import httpx

log = logging.getLogger("triage_engine")

OLLAMA_BASE = "http://localhost:11434"
MODEL_NAME  = "climate-smart-triage:latest"

# WHO IMCI age-adjusted respiratory rate danger thresholds
RR_THRESHOLDS = {"0_2mo": 60, "2_12mo": 50, "1_5y": 40}


def age_rr_threshold(age_months: int) -> int:
    if age_months < 2:  return 60
    if age_months < 12: return 50
    return 40


def describe_age(age_months: int) -> str:
    if age_months < 2:
        return "neonate (%d days old)" % (age_months * 30)
    if age_months < 12:
        return "infant (%d months)" % age_months
    years  = age_months // 12
    months = age_months % 12
    return "%d year%s%s" % (years, "s" if years > 1 else "",
                            " %d months" % months if months else "")


def build_prompt(vitals: Dict, climate: Dict) -> str:
    rr           = vitals.get("respiratory_rate")
    rr_threshold = age_rr_threshold(vitals.get("age_months", 24))
    rr_flag      = (" [ELEVATED — threshold for this age: %d]" % rr_threshold
                    if rr and rr > rr_threshold else "")

    symptoms = vitals.get("symptoms", [])

    template = (
        "You are a paediatric triage assistant helping an ASHA community health worker. "
        "Use the patient data and climate context to give a clear triage decision. "
        "Write in plain English. State urgency first, then reason, then action.\n\n"
        "PATIENT:\n"
        "  Age:               {age}\n"
        "  Weight:            {weight} kg\n"
        "  Temperature:       {temp} C\n"
        "  Respiratory rate:  {rr} breaths/min{rr_flag}\n"
        "  Heart rate:        {hr} bpm\n"
        "  Chief complaint:   {complaint}\n"
        "  Symptoms:          {symptoms}\n\n"
        "CLIMATE CONTEXT:\n"
        "  Ambient temperature:  {amb} C\n"
        "  Humidity:             {humidity}%\n"
        "  Recent event:         {event}\n"
        "  Disease alert:        {alert}\n\n"
        "Triage decision:"
    )

    return template.format(
        age      = describe_age(vitals.get("age_months", 0)),
        weight   = vitals.get("weight_kg", "unknown"),
        temp     = vitals.get("temperature_c", "unknown"),
        rr       = rr or "not counted",
        rr_flag  = rr_flag,
        hr       = vitals.get("heart_rate", "unknown"),
        complaint= vitals.get("chief_complaint", "not stated"),
        symptoms = ", ".join(symptoms) if symptoms else "none reported",
        amb      = climate.get("temperature_c", "unknown"),
        humidity = climate.get("humidity_pct", "unknown"),
        event    = climate.get("recent_event", "none"),
        alert    = climate.get("disease_alert", "none"),
    )


def parse_urgency(text: str) -> str:
    t = text.upper()
    if "IMMEDIATE" in t or "EMERGENCY" in t: return "RED"
    if "URGENT" in t or "HIGH RISK" in t:    return "YELLOW"
    return "GREEN"


async def run_inference(prompt: str, timeout: int = 30) -> str:
    """
    Send prompt to local Ollama daemon.
    Falls back to a safe offline message if Ollama is not running.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{OLLAMA_BASE}/api/generate",
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
    except Exception as exc:
        log.error("Ollama inference failed: %s", exc)
        return (
            "URGENT — AI MODEL UNAVAILABLE\n"
            "Apply WHO IMCI danger sign rules manually. "
            "If any danger sign is present, refer the child immediately."
        )


async def triage(vitals: Dict, climate: Dict) -> Dict:
    """
    Main entry point — called by the FastAPI route and Flutter method channel.
    Returns urgency code (RED / YELLOW / GREEN), full AI text, and short action.
    """
    prompt  = build_prompt(vitals, climate)
    ai_text = await run_inference(prompt)
    urgency = parse_urgency(ai_text)

    action_match = re.search(r"Action[:\s]+(.+)", ai_text, re.IGNORECASE)
    action = (action_match.group(1).strip()
              if action_match else ai_text.split("\n")[0].strip())

    return {
        "urgency":            urgency,
        "triage_output":      ai_text,
        "recommended_action": action,
        "model":              MODEL_NAME,
    }
