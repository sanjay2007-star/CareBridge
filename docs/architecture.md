# System Architecture & Privacy Boundaries

The Consent-Aware EAP Continuity System uses a multi-stage deterministic processing pipeline to ensure that sensitive counselling notes are never transferred to receiving professionals without explicit active client consent.

## Data Processing Pipeline

```
[ Session Records ]
        ↓
[ Information Classification ]  (Rule-based NLP category tags)
        ↓
[ Deterministic Consent Check ] (Explicit status == 'granted' & role match)
        ↓
[ Sensitive Text Filter ]       (Removes unconsented/revoked topics)
        ↓
[ Continuity Engine ]          (Structured summary & confidence scoring)
        ↓
[ Safe Fallback Guardrail ]    (Confidence >= 0.80 -> Authoritative; < 0.60 -> Human Review)
        ↓
[ SQLite DB & Audit Trail ]    (Immutable access & authorization logging)
```

## Mandatory Privacy Boundary Rule

No information may enter a handover summary merely because it appeared in a previous counselling session. It must first pass explicit deterministic consent verification for the specific recipient role.
