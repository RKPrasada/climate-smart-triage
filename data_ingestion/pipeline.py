"""
data_ingestion/pipeline.py  —  ClimateSmartTriage
--------------------------------------------------
Pulls raw data from WHO IMCI guidelines, climate-health research,
and Eastern Ghats seasonal patterns. Builds a clinical knowledge
graph, generates sentence embeddings for RAG retrieval, and writes
JSONL training examples for SLM fine-tuning.

Usage:
    python data_ingestion/pipeline.py --output ./data

Apache 2.0 — see LICENSE
"""

import argparse
import json
import logging
import os
import pickle
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline")


# ---------------------------------------------------------------------------
# 1. WHO IMCI Protocols
# ---------------------------------------------------------------------------

def load_who_protocols() -> List[Dict]:
    """
    Structured paediatric triage protocols from WHO IMCI guidelines 2023.
    In production: parsed from the PDF via PyPDF2 + section heuristics.
    The data structure produced by the PDF parser is identical to this.
    """
    return [
        {
            "condition": "Pneumonia",
            "icd10": "J18",
            "danger_signs": [
                "Respiratory rate above age threshold",
                "Stridor in calm child",
                "Lower chest wall indrawing",
                "Severe acute malnutrition",
            ],
            "age_thresholds": {
                "0_2mo":  {"rr_danger": 60},
                "2_12mo": {"rr_danger": 50},
                "1_5y":   {"rr_danger": 40},
            },
            "action": "URGENT referral",
            "assessment": "Count RR for 60 s; check nasal flaring; check lower chest wall",
            "source": "WHO IMCI 2023",
        },
        {
            "condition": "Severe diarrhoeal dehydration",
            "icd10": "K59.1",
            "danger_signs": [
                "Lethargy or unconscious",
                "Sunken fontanelle",
                "Unable to drink",
                "Skin pinch returns very slowly",
            ],
            "action": "IMMEDIATE referral; start ORS on the way",
            "assessment": "Check hydration: tears, fontanelle, skin turgor, drinking",
            "source": "WHO IMCI 2023",
        },
        {
            "condition": "Fever",
            "icd10": "R50",
            "danger_signs": [
                "Petechial or purpuric rash",
                "Neck stiffness",
                "Altered consciousness",
                "Fever in child under 3 months",
            ],
            "differential": ["Malaria", "Dengue", "Meningitis", "Typhoid"],
            "action": "IMMEDIATE if any danger sign; URGENT otherwise",
            "assessment": "Check rash; assess consciousness (AVPU); check neck stiffness",
            "source": "WHO IMCI 2023",
        },
        {
            "condition": "Neonatal heat stress",
            "icd10": "T67",
            "danger_signs": [
                "Core temperature above 39.5 C",
                "Absent sweating",
                "Altered consciousness",
                "Seizure",
            ],
            "age_risk": "Neonates 0–28 days most vulnerable",
            "action": "IMMEDIATE referral; tepid sponging en route",
            "assessment": "Rectal temperature; feeding; sweating check",
            "source": "GHHIN paediatric guidelines 2023",
        },
        {
            "condition": "Severe acute malnutrition",
            "icd10": "E43",
            "danger_signs": [
                "MUAC below 11.5 cm",
                "Bilateral pitting oedema",
                "Weight-for-height Z below minus 3",
            ],
            "action": "URGENT referral to SAM stabilisation centre",
            "assessment": "Measure MUAC; check oedema; weigh and plot on chart",
            "source": "WHO SAM guidelines 2023",
        },
    ]


# ---------------------------------------------------------------------------
# 2. Climate-health correlations
# ---------------------------------------------------------------------------

def load_climate_insights() -> List[Dict]:
    """
    Published climate-health associations relevant to the Eastern Ghats
    and the South Asian monsoon belt.
    """
    return [
        {
            "relationship": "Humidity above 80% and temperature 25–30 C causes mosquito breeding surge",
            "diseases": ["Malaria", "Dengue"],
            "pediatric_impact": "Children under 5 have highest malaria mortality; cerebral malaria risk",
            "lag": "3–4 weeks (mosquito development cycle)",
            "source": "Lancet Infectious Diseases 2024",
        },
        {
            "relationship": "Post-flood water stagnation causes faecal-oral pathogen contamination",
            "diseases": ["Cholera", "Typhoid", "Cryptosporidiosis"],
            "pediatric_impact": "Severe dehydration in children under 2; acute kidney injury risk",
            "lag": "1–2 weeks post-flood peak",
            "source": "Environmental Health Perspectives 2023",
        },
        {
            "relationship": "Dust storms with AQI above 300 cause airway inflammation and infection",
            "diseases": ["Acute respiratory infection", "Asthma exacerbation"],
            "pediatric_impact": "Acute respiratory distress; bronchospasm",
            "lag": "0–3 days",
            "source": "Environmental Health Perspectives 2022",
        },
        {
            "relationship": "Heat index above 40 C causes neonatal hyperthermia",
            "diseases": ["Heat stroke", "Heat exhaustion"],
            "pediatric_impact": "Neonates cannot sweat; body temperature rises rapidly",
            "lag": "0–2 days",
            "source": "GHHIN 2023",
        },
        {
            "relationship": "Monsoon food gap in weeks 6–8 causes acute malnutrition surge",
            "diseases": ["Severe acute malnutrition"],
            "pediatric_impact": "Wasting peaks when household food stores deplete",
            "lag": "6–8 weeks into monsoon",
            "source": "IPC Andhra Pradesh 2024",
        },
    ]


# ---------------------------------------------------------------------------
# 3. Eastern Ghats seasonal patterns
# ---------------------------------------------------------------------------

def load_seasonal_patterns() -> List[Dict]:
    return [
        {
            "season": "Monsoon (June–September)",
            "climate": {
                "humidity_pct": "above 80",
                "temp_c": "25–30",
                "rainfall_mm_month": "above 500",
            },
            "diseases": ["Malaria", "Dengue", "Diarrhoeal disease", "Leptospirosis"],
            "peak": "Malaria: weeks 4–8 after monsoon onset",
            "chw_action": "Distribute bed nets; suspect malaria for any fever; stock ORS",
        },
        {
            "season": "Heat season (April–May)",
            "climate": {
                "temp_c": "above 40",
                "heat_index_c": "above 45",
                "humidity_pct": "20–40",
            },
            "diseases": ["Neonatal heat stress", "Acute gastroenteritis", "ARI"],
            "peak": "Immediate — 0–2 days after heat index exceeds 40 C",
            "chw_action": "Daily neonatal home visits; advise shade and oral fluids",
        },
        {
            "season": "Post-monsoon (October–November)",
            "climate": {
                "humidity_pct": "60–75",
                "temp_c": "25–35",
                "stagnant_water": "high",
            },
            "diseases": ["Malaria (peak mortality)", "Dengue", "Measles"],
            "peak": "Malaria mortality peaks weeks 3–6 post-monsoon",
            "chw_action": "Intensive case detection; refer any fever with chills immediately",
        },
    ]


# ---------------------------------------------------------------------------
# 4. Knowledge graph
# ---------------------------------------------------------------------------

def build_knowledge_graph(
    protocols: List[Dict],
    insights: List[Dict],
    patterns: List[Dict],
) -> Dict:
    graph: Dict = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "region": "Eastern_Ghats_Paderu_Araku",
            "version": "1.0",
        },
        "entities": {
            "diseases": [p["condition"] for p in protocols],
            "seasons": [p["season"] for p in patterns],
            "climate_triggers": [
                "High humidity", "Heat wave", "Flooding", "Dust storm", "Monsoon",
            ],
            "age_groups": [
                "Neonate (0–28 days)", "Infant (1–11 months)", "Child (1–5 years)",
            ],
        },
        "relations": [],
    }

    for p in protocols:
        for sign in p.get("danger_signs", []):
            graph["relations"].append({
                "source": sign,
                "relation": "INDICATES",
                "target": p["condition"],
                "strength": 0.90,
            })

    for pat in patterns:
        for disease in pat.get("diseases", []):
            graph["relations"].append({
                "source": pat["season"],
                "relation": "ASSOCIATED_WITH",
                "target": disease,
                "strength": 0.88,
            })

    for ins in insights:
        rel = ins.get("relationship", "")
        source = rel.split("causes")[0].strip() if "causes" in rel else rel[:60]
        graph["relations"].append({
            "source": source,
            "relation": "INCREASES_RISK_OF",
            "target": ins.get("diseases", ["Unknown"])[0],
            "strength": 0.85,
            "ref": ins.get("source", ""),
        })

    return graph


# ---------------------------------------------------------------------------
# 5. Training examples
# ---------------------------------------------------------------------------

def build_training_examples(
    protocols: List[Dict],
    patterns: List[Dict],
) -> List[Dict]:
    """
    Returns instruction-following examples in Alpaca format.
    Stage 1 examples teach WHO IMCI clinical alignment.
    Stage 2 examples teach climate-context adjustment.
    """
    examples: List[Dict] = []

    # Stage 1 — clinical alignment
    stage1 = [
        (
            "Patient: 18-month-old, weight 8.5 kg, temperature 39.2 C, "
            "respiratory rate 58 breaths per minute, watery diarrhoea 5 times today, "
            "sunken fontanelle, lethargic",
            "URGENT REFERRAL
"
            "Danger signs present: respiratory rate 58 (normal for this age is under 40), "
            "sunken fontanelle (severe dehydration), lethargy.
"
            "Likely: severe diarrhoeal dehydration with possible concurrent pneumonia.
"
            "Action: refer to health facility within 2 hours. Start ORS immediately. "
            "Keep the child cool.",
        ),
        (
            "Patient: 6-month-old, temperature 37.8 C, cough for 3 days, "
            "respiratory rate 36 breaths per minute, alert, normal fontanelle, drinking well",
            "HOME CARE
"
            "No danger signs. Respiratory rate is normal for this age (under 50). "
            "Alert and drinking well.
"
            "Likely: mild upper respiratory infection.
"
            "Action: continue breastfeeding; return in 5 days or earlier if breathing worsens "
            "or temperature rises above 38 C.",
        ),
        (
            "Patient: 2-day-old neonate, temperature 38.6 C, "
            "poor feeding since yesterday, irritable",
            "IMMEDIATE REFERRAL — EMERGENCY
"
            "Any fever in a child under 3 months is an emergency until serious bacterial "
            "infection is excluded. Risk: sepsis, meningitis.
"
            "Action: refer NOW. Wrap to prevent heat loss during transport.",
        ),
        (
            "Patient: 4-year-old, MUAC 11.0 cm, bilateral ankle oedema, "
            "no appetite for 2 weeks, weight 11 kg",
            "URGENT REFERRAL — SEVERE ACUTE MALNUTRITION
"
            "MUAC below 11.5 cm plus bilateral oedema confirms severe acute malnutrition.
"
            "Action: refer to SAM stabilisation centre. Do not start high-energy feeds "
            "before medical assessment — risk of refeeding syndrome.",
        ),
    ]

    for inp, out in stage1:
        examples.append({
            "instruction": (
                "You are a paediatric triage assistant helping an ASHA community health worker. "
                "Assess the child and give a clear triage decision with the action to take. "
                "Use plain language — the health worker is not a doctor."
            ),
            "input": inp,
            "output": out,
            "stage": "clinical_alignment",
        })

    # Stage 2 — climate integration
    stage2 = [
        (
            "Season: Monsoon week 5. Heavy rain 3 days ago. Stagnant pools visible near the village. "
            "Patient: 18-month-old, temperature 38.5 C, lethargy, weak cry, poor feeding.",
            "HIGH RISK — URGENT REFERRAL
"
            "Climate context: monsoon week 5 is peak malaria season in the Eastern Ghats. "
            "Stagnant water confirms active mosquito breeding.
"
            "Lethargy and poor feeding with fever suggests possible severe malaria, "
            "which can progress to coma within hours.
"
            "Action: refer urgently. Perform malaria rapid test if available. "
            "Paracetamol only for fever — no aspirin.",
        ),
        (
            "Season: Late April heat wave. Heat index 43 C for the past 3 days. "
            "Patient: 10-day-old neonate, temperature 38.9 C, not feeding since morning, "
            "minimal movement, no visible sweating.",
            "IMMEDIATE REFERRAL — NEONATAL HEAT STRESS
"
            "Climate context: heat index 43 C. Neonates cannot regulate body temperature. "
            "This is a medical emergency.
"
            "Signs of heat stroke: high temperature, not feeding, not moving, no sweating.
"
            "Action: while arranging transport, move baby to coolest available place, "
            "remove excess clothing, fan gently, offer expressed breast milk. "
            "Do not immerse in cold water. Refer immediately.",
        ),
        (
            "Season: October post-monsoon. Stagnant water widespread. "
            "Patient: 3-year-old, fever 37.9 C, headache, refusing food for 2 days. No rash.",
            "YELLOW — SAME-DAY ASSESSMENT NEEDED
"
            "Climate context: October is peak malaria and dengue season. "
            "Any fever now needs a malaria rapid test the same day.
"
            "No immediate danger signs but 2 days of food refusal needs review today.
"
            "Action: perform malaria RDT. If positive, refer. "
            "If negative: paracetamol, fluids, return tomorrow or sooner if rash appears.",
        ),
    ]

    for inp, out in stage2:
        examples.append({
            "instruction": (
                "You are a climate-aware paediatric triage assistant. "
                "The local climate context is provided alongside the patient data. "
                "Factor it into your assessment. Give a clear triage decision in plain language."
            ),
            "input": inp,
            "output": out,
            "stage": "climate_integration",
        })

    return examples


# ---------------------------------------------------------------------------
# 6. Embeddings
# ---------------------------------------------------------------------------

def generate_embeddings(texts: List[str], output_path: Path) -> None:
    """
    Production: SentenceTransformer('all-MiniLM-L6-v2').encode(texts)
    Stub returns zero vectors so the pipeline runs without a GPU.
    """
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = {t: model.encode(t).tolist() for t in texts}
        log.info("      Real embeddings generated via SentenceTransformer")
    except ImportError:
        embeddings = {t: [0.0] * 384 for t in texts}
        log.warning("      sentence_transformers not installed — stub embeddings written")

    with open(output_path, "wb") as f:
        pickle.dump(embeddings, f)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(output_dir: str = "./data") -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    log.info("=" * 60)
    log.info("ClimateSmartTriage — Data Ingestion Pipeline")
    log.info("=" * 60)

    log.info("[1/5] Loading WHO IMCI protocols …")
    protocols = load_who_protocols()
    log.info("      %d protocols", len(protocols))

    log.info("[2/5] Loading climate-health correlations …")
    insights = load_climate_insights()
    log.info("      %d correlations", len(insights))

    log.info("[3/5] Loading Eastern Ghats seasonal patterns …")
    patterns = load_seasonal_patterns()
    log.info("      %d patterns", len(patterns))

    log.info("[4/5] Building knowledge graph …")
    graph = build_knowledge_graph(protocols, insights, patterns)
    kg_path = out / "knowledge_graph.json"
    kg_path.write_text(json.dumps(graph, indent=2))
    n_ent = sum(len(v) for v in graph["entities"].values())
    log.info("      %d entities, %d relations → %s", n_ent, len(graph["relations"]), kg_path)

    log.info("[5/5] Generating training examples …")
    examples = build_training_examples(protocols, patterns)
    random.shuffle(examples)
    n_val = max(1, int(len(examples) * 0.10))
    train, val = examples[n_val:], examples[:n_val]

    def write_jsonl(path: Path, rows: List[Dict]) -> None:
        with open(path, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

    write_jsonl(out / "training_examples.jsonl", train)
    write_jsonl(out / "validation_examples.jsonl", val)
    log.info("      %d train / %d validation", len(train), len(val))

    log.info("      Generating embeddings …")
    texts = [p.get("assessment", "") for p in protocols] +             [i.get("relationship", "") for i in insights]
    generate_embeddings([t for t in texts if t], out / "embeddings.pkl")

    summary = {
        "run_at": datetime.now().isoformat(),
        "protocols": len(protocols),
        "insights": len(insights),
        "patterns": len(patterns),
        "train": len(train),
        "validation": len(val),
        "output_dir": str(out),
    }
    (out / "pipeline_summary.json").write_text(json.dumps(summary, indent=2))
    log.info("=" * 60)
    log.info("Done. Output in %s/", out)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClimateSmartTriage data ingestion")
    parser.add_argument("--output", default="./data", help="Output directory")
    args = parser.parse_args()
    run(args.output)
