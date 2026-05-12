# Data Sovereignty Framework
## ClimateSmartTriage — Paderu and Araku Tribal Communities

---

## Principle

The health data of the Poroja, Kondh, and Gadaba tribal communities belongs to
those communities. No researcher, government body, or technology provider can
access, aggregate, or publish this data without explicit, informed consent from
the household it belongs to.

---

## Implementation

### Self-Sovereign Identity

Every enrolled household receives a Decentralised Identifier (DID) anchored to a
Hyperledger Indy ledger operated by ITDA Paderu. The private key stays on the
household's device. Only the household can authorise data access.

### Consent Credentials

Before any data is collected, the household receives a W3C Verifiable Credential
for each distinct use of their data.

| Consent type | What it covers |
|---|---|
| health_data_collection | Recording triage assessments on the device |
| ai_triage_use | Using data to run AI triage on-device |
| federated_learning | Contributing anonymised model updates |
| data_export | Aggregated data in district health reports |

Consent is provided in written Telugu, audio Telugu, and written English.

### Immutable Audit Trail

Every data access is recorded on the Hyperledger Besu blockchain.
Record contains: hashed DID, access type, purpose, timestamp.
No one can delete or alter these records.

### Consent Withdrawal

Any household can withdraw consent at any time.
Within 30 days: credentials revoked, local records deleted, server records removed,
deletion confirmation written to audit log.

### Community Governance

A Village Health Sanitation and Nutrition Committee (VHSNC) representative
sits on the data governance board, which must approve any new data use before
it is implemented.

---

## What We Do Not Do

- We do not collect biometric data
- We do not share raw patient records with third parties
- We do not use health data for commercial purposes
- We do not require sync for offline emergency features

---

## Legal Basis

India Personal Data Protection framework (2023)
WHO ethical guidelines for health research with indigenous communities
UNICEF child safeguarding standards
