# Consent-Aware EAP Continuity & Handover System

An end-to-end web application for Employee Assistance Programmes (EAP) supporting a distributed workforce across Remote, Hybrid, and On-site modalities.

The system creates a **consent-aware continuity summary** during counsellor and social worker handovers, ensuring that sensitive information unapproved by client consent remains strictly protected while authorized context is transferred seamlessly to prevent unnecessary client repetition.

---

## Key Features

1. **Deterministic Consent Engine**: Code-enforced privacy filtering rules check explicit client consent for each category (`workplace`, `financial`, `family`, `wellbeing`, `housing`, `legal_support`) and recipient role before text generation.
2. **Safe Processing Pipeline**: Session Records → Information Classification → Consent Verification → Role/Permission Check → Sensitive Filtering → Continuity Summary → Confidence Score Calculation → Safe Summary OR Human Review Fallback.
3. **Confidence Scoring & Safe Fallbacks**: Calculates scores based on session recency, consent completeness, goal availability, and conflicting note detection. Scores < 0.60 trigger safe fallback messages.
4. **Staff Capacity Management**: Tracks `maximum_active_cases`, `current_active_cases`, and places overflow handovers on `WAITLIST`.
5. **Role-Based Access Control (RBAC)**: Supports Client, Counsellor, Social Worker, and Administrator personas. Administrators are strictly restricted from viewing raw counselling notes (HTTP 403 Forbidden logged in Audit Trail).
6. **Empirical Baseline vs Prototype Evaluation**: Includes experiment evaluation script measuring Repetition Reduction (91.52%), Consent Violation Rate (0.0%), Summary Completeness (86.55%), and Fairness across Work Mode & Language Group dimensions.
7. **Interactive Demo Scenario (Client C001)**: Live step-by-step demonstration of transfer from Counsellor (COUNS_001) to Social Worker (SOC_001) where Financial notes are included while Family notes are completely excluded.

---

## Architecture Overview

```
[ React Dashboard (Vite/Tailwind/Recharts) ]
               ↓
[ FastAPI REST Endpoints & RBAC Middleware ]
               ↓
[ Deterministic Consent Engine & Text Classifier ]
               ↓
[ Continuity Summary & Confidence Guardrails ]
               ↓
[ SQLite Database & Audit Trail Logging ]
```

---

## Quick Start Guide

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate synthetic dataset (200 clients, 15 counsellors, 8 social workers, 708 sessions)
python data/generate_synthetic_data.py

# Run baseline vs prototype evaluation experiment
python evaluation/experiment.py

# Run automated test suite
pytest tests/

# Start FastAPI backend server
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Navigate to `http://localhost:3000` in your web browser.

---

## Experimental Evaluation Results (N = 200 Handovers)

| Metric | Baseline | Prototype | Target Status |
|---|---|---|---|
| Repetition Rate | 75.95% | 6.44% | Lower than baseline |
| Repetition Reduction | 0.0% | **91.52%** | PASSED (>= 50%) |
| Consent Violation Rate | 15.0% | **0.0%** | PASSED (Target: 0.0%) |
| Summary Completeness | 45.0% | **86.55%** | PASSED (>= 85.0%) |
| Pending Action Recall | 30.0% | **75.32%** | Measured |
| Human Review Rate | N/A | **8.50%** | Report |

---

## Documentation

- [Architecture & Pipeline Specs](docs/architecture.md)
- [Database Schemas & Models](docs/data_schema.md)
- [Stakeholder Assumptions](docs/stakeholder_assumptions.md)
- [Risk Register (11 Risks & Safeguards)](docs/risk_register.md)
- [User Guide & Reproducible Commands](docs/user_guide.md)
- [Experiment Results](docs/experiment_results.md)
