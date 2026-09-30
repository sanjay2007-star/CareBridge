# System Architecture, Concrete Implementation Code & API Schemas

The **Consent-Aware Employee Assistance Programme (EAP) Continuity & Handover System** uses a multi-stage deterministic processing pipeline to ensure sensitive counselling notes are never transferred to receiving staff without explicit active client consent.

---

## 1. Data Processing Pipeline Architecture

```
[ Session Records ]
        ↓
[ Information Classification ]  (Rule-based NLP category tags: workplace, financial, family, wellbeing, housing, legal)
        ↓
[ Deterministic Consent Check ] (Explicit status == 'granted' & recipient role match)
        ↓
[ Sensitive Text Filter ]       (Removes unconsented/revoked topic sentences)
        ↓
[ Section 10 Conflict Engine ]  (Rule-based & semantic contradiction scanner across session history)
        ↓
[ Continuity Engine ]          (Structured summary & confidence scoring: 1.00 base score)
        ↓
[ Safe Fallback Guardrail ]    (Confidence >= 0.60 -> Authoritative Summary; < 0.60 -> Human Review Fallback)
        ↓
[ SQLite DB & Audit Trail ]    (Immutable access & HTTP 403 authorization logging)
```

---

## 2. Concrete Implementation Code Samples

### A. Deterministic Consent Engine (`backend/consent/consent_engine.py`)

```python
import re
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from backend.models import ConsentRecord

CATEGORY_KEYWORDS = {
    "workplace": ["workplace", "workload", "burnout", "job", "career", "manager", "team", "overtime", "deadline"],
    "financial": ["financial", "debt", "budget", "loan", "expenses", "cost of living", "salary", "monetary", "money"],
    "family": ["family", "marital", "spouse", "marriage", "childcare", "parents", "child", "bereavement", "domestic"],
    "wellbeing": ["anxiety", "sleep", "stress", "mindfulness", "panic", "self-care", "wellbeing", "mental health"],
    "housing": ["housing", "lease", "landlord", "relocation", "tenancy", "tenant", "rent escalation"],
    "legal_support": ["legal", "contract", "estate", "court", "attorney", "lawyer", "divorce proceedings"],
    "general_progress": ["progress", "goals", "session", "check-in", "satisfaction", "improvement"]
}

def is_category_consented(db: Session, client_id: str, category: str, recipient_role: str) -> bool:
    """
    DETERMINISTIC CONSENT CHECK:
    Privacy-by-default: Returns True ONLY if explicit granted record exists matching recipient role.
    """
    records = db.query(ConsentRecord).filter(
        ConsentRecord.client_id == client_id,
        ConsentRecord.information_category == category
    ).all()

    if not records:
        return False

    for rec in records:
        if rec.consent_status == "granted" and rec.revoked_at is None:
            allowed = rec.allowed_recipient_role.lower()
            target_role = recipient_role.lower()
            if allowed == "all" or allowed == target_role:
                return True
    return False

def filter_session_data(db: Session, client_id: str, session_summary: str, recipient_role: str) -> Tuple[str, List[str], List[str]]:
    """Filters text sentences based on explicit client category consent."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', session_summary) if s.strip()]
    approved_sentences, approved_cats, restricted_cats = [], set(), set()

    for sentence in sentences:
        sentence_lower = sentence.lower()
        cats = {cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in sentence_lower for kw in kws)} or {"general_progress"}
        sentence_consented = True
        for cat in cats:
            if is_category_consented(db, client_id, cat, recipient_role):
                approved_cats.add(cat)
            else:
                restricted_cats.add(cat)
                sentence_consented = False
        if sentence_consented:
            approved_sentences.append(sentence)

    return " ".join(approved_sentences), list(approved_cats), list(restricted_cats)
```

---

### B. Handover Summary Generator (`backend/handover/continuity_engine.py`)

```python
from datetime import datetime
from backend.models import SessionRecord, ClientGoal, PendingAction
from backend.consent.consent_engine import filter_session_data, is_category_consented
from backend.handover.conflict_engine import detect_conflicts

def generate_prototype_summary(db: Session, client_id: str, to_staff_role: str):
    sessions = db.query(SessionRecord).filter(SessionRecord.client_id == client_id).order_by(SessionRecord.session_date.desc()).all()
    goals = db.query(ClientGoal).filter(ClientGoal.client_id == client_id, ClientGoal.goal_status == "Active").all()
    actions = db.query(PendingAction).filter(PendingAction.client_id == client_id, PendingAction.status != "Completed").all()

    # Section 10 Conflict Detection
    session_dicts = [{"session_id": s.session_id, "session_date": s.session_date, "session_summary": s.session_summary} for s in sessions]
    has_conflict, conflict_penalty, conflict_flags = detect_conflicts(session_dicts)

    combined_approved_text, all_approved_cats, all_restricted_cats = [], set(), set()
    for sess in sessions:
        filtered_text, app_cats, restr_cats = filter_session_data(db, client_id, sess.session_summary, to_staff_role)
        if filtered_text:
            combined_approved_text.append(f"[{sess.session_date}]: {filtered_text}")
        all_approved_cats.update(app_cats)
        all_restricted_cats.update(restr_cats)

    confidence, review_reasons = 1.0, []
    if has_conflict:
        confidence -= (conflict_penalty if conflict_penalty > 0 else 0.30)
        review_reasons.append("Conflicting clinical information detected across session history.")

    if not approved_goals:
        confidence -= 0.15
        review_reasons.append("No active consent-approved goals found.")

    confidence = round(max(0.0, min(1.0, confidence)), 2)
    requires_human_review = confidence < 0.60 or has_conflict

    if requires_human_review:
        summary_text = f"⚠️ SAFE FALLBACK TRIGGERED\nInsufficient verified information for safe summary.\nReview Reasons: {'; '.join(review_reasons)}"
    else:
        summary_text = f"Structured Continuity Summary for Client {client_id}...\n"

    return summary_text, confidence, requires_human_review, review_reasons, list(all_approved_cats), list(all_restricted_cats)
```

---

## 3. Section 10: Conflict Detection Algorithm Details

Section 10 addresses contradictory session notes or clinical records (e.g. conflicting relocation plans, employment changes, or divergent clinical stress indicators).

### Algorithmic Processing Pipeline

1. **Chronological Session Ingestion**: Historical session records are sorted chronologically by `session_date`.
2. **Rule-Based Opposing Keyword Pair Scanning**: Pair-wise evaluation detects mutually exclusive statements across session pairs $(S_i, S_j)$:
   - **Employment Relocation**: `relocate` / `transfer overseas` vs `remain on-site` / `local branch`
   - **Employment Status**: `full time` / `continuing` vs `resigned` / `terminated`
   - **Clinical Stress Trajectory**: `severe burnout` / `extreme pressure` vs `no burnout` / `minimal stress`
   - **Substance Use & Safety**: `sober` / `no substance use` vs `substance relapse` / `heavy drinking`
3. **Semantic Contradiction & Vector Sentiment Scoring**: Calculates semantic divergence score $\Delta S \in [0.0, 1.0]$:
   $$\text{Penalty} = \begin{cases} 
   0.40 & \text{if Severity = CRITICAL (Safety / Work status contradiction)} \\ 
   0.30 & \text{if Severity = HIGH (Clinical trajectory contradiction)} \\ 
   0.15 & \text{if Severity = MEDIUM (Goal / preference contradiction)}
   \end{cases}$$
4. **Human Review Guardrail Flagging**: Any flagged conflict automatically sets `requires_human_review = True` and triggers the `⚠️ SAFE FALLBACK TRIGGERED` guardrail state.

---

## 4. API Endpoint Schemas

### Endpoint 1: `POST /api/consent/check`

#### Request Schema (`ConsentCheckRequest`):
```json
{
  "client_id": "C001",
  "information_category": "financial",
  "recipient_role": "social_worker"
}
```

#### Response Schema (`ConsentCheckResponse`):
```json
{
  "client_id": "C001",
  "information_category": "financial",
  "recipient_role": "social_worker",
  "is_consented": true,
  "consent_status": "granted"
}
```

---

### Endpoint 2: `POST /api/consent/filter`

#### Request Schema (`ConsentFilterRequest`):
```json
{
  "client_id": "C001",
  "session_summary": "Client discussed financial stress and family conflict.",
  "recipient_role": "social_worker"
}
```

#### Response Schema (`ConsentFilterResponse`):
```json
{
  "client_id": "C001",
  "recipient_role": "social_worker",
  "filtered_text": "Client discussed financial stress.",
  "approved_categories": ["financial"],
  "restricted_categories": ["family"]
}
```

---

### Endpoint 3: `POST /api/handovers/generate`

#### Request Schema (`HandoverGenerationRequest`):
```json
{
  "client_id": "C001",
  "from_staff_id": "COUNS_001",
  "to_staff_id": "SOC_001"
}
```

#### Response Schema (`HandoverSummaryResponse`):
```json
{
  "client_id": "C001",
  "from_staff_id": "COUNS_001",
  "to_staff_id": "SOC_001",
  "recipient_role": "social_worker",
  "baseline_summary": "[BASELINE HANDOVER SUMMARY] Client ID: C001...",
  "prototype_summary": "Structured Continuity Summary for Client C001...",
  "confidence_score": 0.95,
  "requires_human_review": false,
  "review_reasons": [],
  "approved_categories": ["financial", "wellbeing"],
  "restricted_categories": ["family"]
}
```

---

### Endpoint 4: `POST /api/conflict/detect`

#### Request Schema (`ConflictCheckRequest`):
```json
{
  "client_id": "C001"
}
```

#### Response Schema (`ConflictCheckResponse`):
```json
{
  "client_id": "C001",
  "has_conflict": true,
  "max_confidence_penalty": 0.40,
  "conflict_flags": [
    {
      "session_id_1": "SESS_CONF_1",
      "session_date_1": "2026-08-01",
      "session_id_2": "SESS_CONF_2",
      "session_date_2": "2026-08-10",
      "conflict_category": "Employment Status",
      "severity": "CRITICAL",
      "description": "Contradictory relocation vs local retention plans across sessions.",
      "confidence_penalty": 0.40
    }
  ]
}
```
