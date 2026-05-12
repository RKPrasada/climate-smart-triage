# ClimateSmartTriage

**Offline-first AI triage for children in climate-vulnerable communities**

> Built for ASHA workers in the tribal regions of Paderu and Araku Valley, Andhra Pradesh, India.
> Submitted to the [UNICEF Venture Fund — Climate & Health 2026](https://www.unicef.org/innovation/call-for-application-climate-and-health-2026)

---

## The Problem

Community health workers in the Eastern Ghats lose mobile connectivity more than 70% of the time. During monsoon floods and heatwaves — the exact moments when children get sick — every cloud-based triage tool fails completely.

Existing apps also treat every fever the same way, regardless of whether a flood happened three days ago or whether the heat index has been above 40°C all week. Children under five in these tribal communities carry a disproportionate disease burden: malaria surges four weeks after the monsoon starts, waterborne diarrhea follows flooding, and neonatal heat stress peaks in April and May. Health workers have no tools that work offline, factor in the climate around them, or protect tribal communities from having their health data taken without consent.

---

## What It Does

A health worker opens the app on a standard Android phone. No internet needed. She enters a child's age, weight, temperature, breathing rate, and symptoms. The app already knows the local climate — it cached a forecast the last time any connectivity was available.

If it is monsoon week five, the app weights malaria and diarrheal disease higher in its assessment. If the heat index crossed 40°C yesterday, it flags any newborn in the next home visit for heat stress checks before symptoms appear.

The AI returns a triage recommendation in plain Telugu or English with a clear urgency level and action. The reasoning is shown in simple language so the health worker understands why, not just what.

When connectivity returns, the app syncs anonymised disease counts to the district health system. No raw patient data leaves the device without explicit household consent.

---

## Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| On-device AI | Google Gemma 2B — 4-bit quantised (GGUF) | Runs on 6 GB RAM phones, 3–5 second response, no internet |
| Inference engine | llama.cpp via Ollama | Cross-platform, zero cloud dependency |
| AI fine-tuning | HuggingFace Transformers + QLoRA | 4-bit quantisation fits on a single consumer GPU |
| Vector search | Milvus (local) | On-device retrieval-augmented generation |
| Mobile app | Flutter (Dart) | Single codebase, small APK, excellent offline support |
| Local storage | Hive + Drift | Encrypted on-device database, conflict-free sync |
| Backend API | FastAPI (Python) | Async, auto-documented, handles concurrent device syncs |
| Task queue | Celery + Redis | Federated learning jobs run without blocking the API |
| Database | PostgreSQL | Health records, aggregated disease trends |
| Identity | Hyperledger Indy | Self-sovereign identity — households own their health data |
| Audit log | Hyperledger Besu | Every data access recorded in an immutable smart contract |
| Localisation | GetX + Easy Localization | Telugu (native-speaker reviewed), English, Hindi (Phase 2) |

**Blockchain clarification:** Blockchain does not store health records — PostgreSQL does that. Hyperledger Indy handles household identity (who owns the data). Hyperledger Besu records immutable audit logs (who accessed what and when). This keeps the system fast while making data governance transparent and verifiable.

---

## Repository Structure

```
climate-smart-triage/
│
├── README.md
├── LICENSE                              Apache 2.0
├── requirements.txt
├── .gitignore
│
├── data_ingestion/
│   ├── pipeline.py                      Main orchestration — runs the full ingestion
│   └── sample_output/
│       ├── knowledge_graph.json         Sample output: Eastern Ghats, 150+ relations
│       └── training_examples.jsonl      10 sample fine-tuning examples
│
├── model/
│   ├── config/
│   │   └── lora_config.yaml             QLoRA training configuration
│   ├── inference/
│   │   └── triage_engine.py             Wraps Ollama, builds climate-aware prompts
│   └── prompts/
│       └── triage_prompt_template.txt   Base prompt with patient + climate slots
│
├── backend/
│   ├── main.py                          FastAPI app entry point
│   ├── routes/
│   │   ├── triage.py                    POST /triage
│   │   ├── climate.py                   GET  /climate-alerts
│   │   ├── consent.py                   POST /consent/register and /consent/issue
│   │   ├── federated.py                 POST /federated-gradient
│   │   └── export.py                    GET  /export/fhir and /export/csv
│   ├── models/
│   │   └── patient.py                   Pydantic schemas
│   ├── blockchain/
│   │   ├── indy_client.py               Hyperledger Indy: DIDs and credentials
│   │   └── besu_audit.py                Hyperledger Besu: audit log
│   ├── federated/
│   │   └── aggregator.py                Gradient aggregation (Celery task)
│   └── tests/
│       └── test_triage_route.py         Smoke tests
│
├── mobile/
│   ├── lib/
│   │   ├── main.dart                    App entry, routing, localisation
│   │   ├── screens/
│   │   │   ├── home_screen.dart         Climate alert banner + quick actions
│   │   │   ├── triage_form.dart         Patient vitals entry
│   │   │   ├── triage_result.dart       AI output display
│   │   │   └── history_screen.dart      Past triages with sync status
│   │   ├── services/
│   │   │   ├── ai_service.dart          Calls Ollama on-device
│   │   │   ├── sync_service.dart        WatermelonDB sync
│   │   │   └── consent_service.dart     DID and credential management
│   │   └── i18n/
│   │       ├── en.json                  English strings
│   │       └── te.json                  Telugu strings (native-speaker reviewed)
│   └── pubspec.yaml
│
├── blockchain/
│   ├── indy/
│   │   ├── docker-compose.yml           Local Indy test ledger
│   │   └── schema_definitions/
│   │       └── consent_schema.json      W3C VC schema for consent credentials
│   └── besu/
│       ├── docker-compose.yml           Local Besu node
│       └── contracts/
│           └── AuditLog.sol             Solidity smart contract for audit logging
│
├── docs/
│   ├── clinical/
│   │   └── triage_protocols.md          WHO IMCI rules as implemented
│   └── governance/
│       └── data_sovereignty.md          Tribal data ownership framework
│
├── deployment/
│   ├── docker-compose.yml               Full stack: API + DB + Redis + Ollama
│   └── Dockerfile.api
│
└── scripts/
    ├── setup.sh                         One-command dev setup
    └── run_tests.sh                     Run all tests
```

---

## Quick Start

### What you need

- Python 3.10 or later
- Flutter 3.x
- Docker and Docker Compose
- [Ollama](https://ollama.ai) installed locally

### 1. Clone

```bash
git clone https://github.com/[your-org]/climate-smart-triage.git
cd climate-smart-triage
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the AI model

```bash
ollama pull gemma:2b-instruct-q4_K_M
```

This downloads the 4-bit quantised model (about 1.8 GB). Only needed once. The model runs entirely on-device — no API key, no internet required after download.

### 4. Run the data ingestion pipeline

```bash
python data_ingestion/pipeline.py --output ./data
```

This produces `data/knowledge_graph.json`, `data/training_examples.jsonl`, and `data/embeddings.pkl`.

### 5. Start the backend

```bash
docker-compose -f deployment/docker-compose.yml up
```

API available at `http://localhost:5000`
Interactive docs at `http://localhost:5000/docs`

### 6. Test a triage

```bash
curl -X POST http://localhost:5000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{
    "household_did": "did:indy:paderu:test001",
    "patient_vitals": {
      "age_months": 18,
      "weight_kg": 8.5,
      "temperature_c": 39.2,
      "respiratory_rate": 58,
      "heart_rate": 135,
      "chief_complaint": "fever and loose stools",
      "symptoms": ["fever", "diarrhea", "lethargy"]
    },
    "climate_context": {
      "temperature_c": 28,
      "humidity_pct": 85,
      "recent_event": "heavy rainfall 3 days ago",
      "disease_alert": "post-monsoon diarrheal surge"
    }
  }'
```

### 7. Run the tests

```bash
bash scripts/run_tests.sh
```

### 8. Run the Flutter app

```bash
cd mobile
flutter pub get
flutter run
```

Requires an Android device or emulator with at least 6 GB RAM for on-device inference.

---

## AI Model — Fine-tuning

The base model is Google Gemma 2B (instruction-tuned, Apache 2.0 licence). We fine-tune it in two stages using QLoRA, which fits on a single GPU with 6 GB VRAM.

**Stage 1 — Clinical alignment (approx. 48 hours)**

Trains the model to follow WHO IMCI paediatric triage protocols correctly. Dataset: 10,000 instruction-following examples derived from WHO guidelines covering pneumonia, diarrhoeal dehydration, fever, heat stress, and severe malnutrition.

**Stage 2 — Climate integration (approx. 24 hours)**

Teaches the model to adjust triage risk based on the local climate context. Dataset: 5,000 examples linking the monsoon, heat season, and post-monsoon patterns of the Eastern Ghats to disease likelihood shifts.

```bash
# Stage 1
python model/train.py --stage 1 \
  --base-model google/gemma-2b-it \
  --data data/training_examples.jsonl \
  --config model/config/lora_config.yaml

# Stage 2 (starts from Stage 1 checkpoint)
python model/train.py --stage 2 \
  --checkpoint ./models/stage1_checkpoint \
  --data data/training_examples.jsonl \
  --config model/config/lora_config.yaml
```

After training, convert to GGUF for Ollama:

```bash
# Convert and quantise to 4-bit
python scripts/quantise.py --model-dir ./models/stage2_checkpoint
# Final size: approx. 1.8 GB
# Inference on Snapdragon 695 (6 GB RAM): 3–5 seconds
```

---

## Blockchain — Data Sovereignty

Every household enrolled in the system receives a Decentralised Identifier (DID) anchored to a Hyperledger Indy ledger operated by ITDA Paderu. They control who can access their health data cryptographically — not by trusting a company or a government, but through their own private key stored on their device.

Consent is stored as a W3C Verifiable Credential. Every data access event is written to a Hyperledger Besu smart contract — permanently and tamper-proof.

**Start the local test environment:**

```bash
# Identity ledger
docker-compose -f blockchain/indy/docker-compose.yml up

# Audit log chain
docker-compose -f blockchain/besu/docker-compose.yml up
```

**Register a household:**

```python
from backend.blockchain.indy_client import register_household

did = await register_household(
    household_id="HH_PADERU_001",
    village="Munchingput",
    audio_consent_hash="sha256_of_telugu_audio_recording"
)
# Returns: did:indy:paderu:abc123def456
```

**Deploy the audit log smart contract:**

```bash
cd blockchain/besu/contracts
npx hardhat run scripts/deploy.js --network localhost
```

---

## Federated Learning

Devices never send raw patient data to the server. Each device trains locally on its own triage history and sends only the model gradient — the mathematical update, not the underlying records. The server aggregates gradients from 50 or more devices and applies the combined update to the global model. Individual patient data cannot be reconstructed from a gradient.

The AI gets better over time using real data from Paderu and Araku without that data ever leaving the community.

---

## Data Export

All exports are automatically de-identified — household IDs, names, and precise locations are stripped, data is aggregated by week and facility, and export requires a valid consent credential.

| Endpoint | Format | Use |
|----------|--------|-----|
| `GET /export/fhir` | HL7 FHIR R4 | DHIS2 integration, hospital systems |
| `GET /export/csv` | CSV | Researcher analysis, NGO reporting |

---

## Languages

The app ships with English and Telugu. Telugu strings were reviewed by a native speaker — not machine-translated. Adding a new language requires only a new JSON file in `mobile/lib/i18n/` and a one-line config change. Audio narration is available for low-literacy users via the `flutter_tts` plugin.

---

## Data Governance

This project handles health data belonging to children and tribal communities.

- No biometric data collected (no faces, no fingerprints)
- Households control their data through cryptographic identity
- Every data access is permanently logged on the blockchain
- Consent can be withdrawn at any time; deletion completed within 30 days
- The AI gives a recommendation — the clinical decision always belongs to the health worker
- Accuracy is monitored monthly; deployment pauses if it drops below 85%
- All code is Apache 2.0 — anyone can audit it

Full governance documentation: [docs/governance/data_sovereignty.md](docs/governance/data_sovereignty.md)

---

## Project Status

| Component | Status |
|-----------|--------|
| Data ingestion pipeline | Working and tested |
| AI inference on-device (Ollama + Gemma 2B) | Working — 3–5 s confirmed on device |
| FastAPI backend (all routes defined) | Working — tests passing |
| Flutter app (home, triage form, result screens) | In progress |
| Telugu localisation | Strings complete, native review in progress |
| SLM fine-tuning (clinical + climate) | Training data ready; GPU run scheduled |
| Blockchain identity (Indy) | Local test environment running |
| Audit log smart contract (Besu) | Contract written; deployment pending |
| DHIS2 integration | Planned Month 4–6 |
| Clinical validation (n=500) | Planned Month 4–6 with paediatric partner |

---

## Roadmap

**Month 3** — Pilot-ready app deployed to 10 ASHA workers at one facility in Paderu. 500 triage cases collected.

**Month 6** — Clinical validation complete (target: 85%+ accuracy vs paediatrician). Federated learning running. DHIS2 integrated.

**Month 9** — 50 active ASHA workers across 8–10 facilities. Weekly model updates.

**Month 12** — 100+ ASHA workers. Fine-tuned model published on HuggingFace under Apache 2.0. Independent evaluation report submitted.

---

## Contributing

We welcome:

- Clinical feedback on triage protocols (paediatricians familiar with Eastern Ghats disease burden especially)
- Telugu language review
- Android testing on low-RAM devices (4–6 GB)
- Hyperledger Indy / Besu experience
- Flutter accessibility improvements

Open an issue or email [your contact email].

---

## Licence

Apache 2.0 — see [LICENSE](LICENSE)

You can use, modify, and distribute this code freely, including for commercial purposes, as long as you include the licence notice. State health ministries, NGOs, and researchers are explicitly encouraged to adapt this for their own regions and disease contexts.

---

## Citation

```
ClimateSmartTriage (2026).
Offline-first AI triage for children in climate-vulnerable communities.
GitHub: https://github.com/[your-org]/climate-smart-triage
UNICEF Venture Fund Application — Climate & Health Call 2026.
```

---

## Contact

**Project lead:** [Prasada Ravi Kumar]
**Email:** [rkprasada@gmail.com]
**Organisation:** [Jasan Green Earth Charitable Trust], Andhra Pradesh, India

*This project is seeking $100,000 USD equity-free funding from the UNICEF Venture Fund to take the system from working prototype to 100 ASHA workers actively triaging children in Paderu and Araku by December 2026.*
