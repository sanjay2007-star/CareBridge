# Consent-Aware EAP Continuity & Handover System

An end-to-end web application for Employee Assistance Programmes (EAP) supporting a distributed workforce across Remote, Hybrid, and On-site modalities.

The system creates a **consent-aware continuity summary** during counsellor and social worker handovers, ensuring sensitive information unapproved by client consent remains strictly protected while authorized context is transferred seamlessly to prevent unnecessary client repetition.

---

## 1. System Architecture & Key Innovations

1. **Deterministic Consent Engine**: Code-enforced privacy filtering rules check explicit client consent for each category (`workplace`, `financial`, `family`, `wellbeing`, `housing`, `legal_support`) and recipient role before summary text generation.
2. **Empirical Baseline Benchmarks**: Direct comparison of Naive Baseline vs Consent-Aware Prototype across $N = 200$ handovers (**91.52% Repetition Reduction**, **0.0% Consent Violation Rate**, **86.55% Summary Completeness**, **19.6ms latency**).
3. **Initial Synthetic Dataset Distributions**: Structured demographic distributions across Work Modes (Remote: 34%, Hybrid: 34%, On-site: 32%), Languages (English: 45%, Multilingual: 55%), Age Groups, 708 Clinical Sessions (Low/Medium/High sensitivity), and 1,180 Consent Records (65% Granted, 15% Revoked, 20% Unconfigured).
4. **Section 10 Conflict Detection Algorithm**: Multi-stage rule & semantic scanner evaluating session history for contradictory clinical or operational statements (relocation, employment changes, substance safety, stress divergence). Automatically assigns confidence penalties and forces mandatory Human Review when contradictions occur.
5. **Multi-Layered Error Boundaries & RBAC**: HTTP 403 Forbidden enforcement on administrator raw note access, automatic DB transaction rollbacks, staff capacity waitlisting, and Safe Fallback guardrails (Confidence $< 0.60$).

---

## 2. Quick Start Guide

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate synthetic dataset (200 clients, 15 counsellors, 8 social workers, 708 sessions)
python data/generate_synthetic_data.py

# Run baseline vs prototype evaluation experiment
python evaluation/experiment.py

# Run automated test suite (9 unit & integration tests)
pytest tests/

# Start FastAPI backend server (Port 8000)
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000` in your web browser.

---

## 3. Database Schema Entity Documentation

The database is built on SQLite with SQLAlchemy ORM models (`backend/models.py`).

| Entity / Table | Column / Attribute | Data Type | Key Constraints | Description / Business Logic |
|---|---|---|---|---|
| **`clients`** | `client_id` | String | Primary Key | Unique client identifier (e.g., `C001`) |
| | `age_group` | String | Non-Null | Demographic group (`18-25`, `26-35`, `36-50`, `51+`) |
| | `work_mode` | String | Non-Null | Work modality (`Remote`, `Hybrid`, `On-site`) |
| | `preferred_language` | String | Non-Null | Language preference (`English-primary`, `Multilingual`) |
| | `region` | String | Non-Null | Geographic region (`North America`, `EMEA`, `APAC`, `LATAM`) |
| | `created_at` | DateTime | Default `utcnow` | Client registration timestamp |
| **`sessions`** | `session_id` | String | Primary Key | Unique session identifier (e.g., `SESS_0001`) |
| | `client_id` | String | Foreign Key | Client reference |
| | `counsellor_id` | String | Foreign Key | Counsellor staff ID |
| | `session_date` | String | Non-Null | Date formatted `YYYY-MM-DD` |
| | `session_summary` | Text | Non-Null | Confidential raw counselling notes |
| | `sensitivity_level` | String | Non-Null | Sensitivity rating (`Low`, `Medium`, `High`) |
| **`consent_records`** | `consent_id` | String | Primary Key | Unique consent decision identifier |
| | `client_id` | String | Foreign Key | Client reference |
| | `information_category`| String | Non-Null | Category (`workplace`, `financial`, `family`, `wellbeing`, `housing`, `legal_support`) |
| | `allowed_recipient_role`| String | Non-Null | Recipient restriction (`counsellor`, `social_worker`, `all`) |
| | `consent_status` | String | Non-Null | Status (`granted`, `revoked`) |
| | `granted_at` | DateTime | Non-Null | Consent grant timestamp |
| | `revoked_at` | DateTime | Nullable | Consent revocation timestamp |
| **`client_goals`** | `goal_id` | String | Primary Key | Goal identifier |
| | `client_id` | String | Foreign Key | Client reference |
| | `goal_category` | String | Non-Null | Goal category key |
| | `goal_description` | Text | Non-Null | Goal statement |
| | `goal_status` | String | Non-Null | Status (`Active`, `Achieved`, `Paused`) |
| **`pending_actions`** | `action_id` | String | Primary Key | Follow-up action ID |
| | `client_id` | String | Foreign Key | Client reference |
| | `assigned_role` | String | Non-Null | Assigned staff role (`counsellor`, `social_worker`) |
| | `action_description` | Text | Non-Null | Follow-up task details |
| | `priority` | String | Non-Null | Priority level (`High`, `Medium`, `Low`) |
| | `due_date` | String | Non-Null | Due date formatted `YYYY-MM-DD` |
| | `status` | String | Non-Null | Action status (`Pending`, `In Progress`, `Completed`) |
| **`handover_records`** | `handover_id` | String | Primary Key | Handover record ID |
| | `client_id` | String | Foreign Key | Client reference |
| | `from_staff_id` | String | Foreign Key | Source staff member |
| | `to_staff_id` | String | Foreign Key | Destination staff member |
| | `handover_status` | String | Non-Null | Status (`Approved`, `Human Review Required`, `Waitlisted`) |
| | `confidence_score` | Float | Non-Null | Score rating ($0.00$ to $1.00$) |
| | `requires_human_review`| Boolean | Non-Null | Guardrail fallback flag |
| | `baseline_summary` | Text | Non-Null | Naive unfiltered baseline text |
| | `prototype_summary` | Text | Non-Null | Consent-filtered safe continuity text |
| **`audit_logs`** | `audit_id` | String | Primary Key | Audit event ID |
| | `user_id` | String | Non-Null | User performing action |
| | `client_id` | String | Nullable | Target client ID |
| | `action` | String | Non-Null | Action event type |
| | `resource_type` | String | Non-Null | Entity type (`CLIENT`, `SESSION`, `CONSENT`, `HANDOVER`) |
| | `timestamp` | DateTime | Non-Null | Event timestamp |
| | `result` | String | Non-Null | Access result (`SUCCESS`, `FORBIDDEN`) |
| **`staff_capacity`** | `staff_id` | String | Primary Key | Staff identifier (e.g., `COUNS_001`, `SOC_001`) |
| | `role` | String | Non-Null | Staff role (`counsellor`, `social_worker`, `admin`) |
| | `maximum_active_cases`| Integer | Non-Null | Maximum workload cap |
| | `current_active_cases`| Integer | Non-Null | Active case count |
| | `available_slots` | Integer | Non-Null | Open capacity slots |

---

## 4. API Endpoints Specification

FastAPI REST endpoints provided by `backend/main.py`:

### Client & Profile Endpoints
- **`GET /api/clients`**: Lists workforce clients with optional `work_mode` or `language` filtering.
- **`GET /api/clients/{client_id}`**: Retrieves client profile details and logs audit event.

### Consent Engine Endpoints
- **`GET /api/clients/{client_id}/consents`**: Retrieves consent records for a client.
- **`POST /api/consents/update`**: Updates or creates a consent decision (`granted` / `revoked`).
- **`POST /api/consent/check`**: Evaluates whether explicit consent exists for a given category & recipient role (`ConsentCheckRequest` $\rightarrow$ `ConsentCheckResponse`).
- **`POST /api/consent/filter`**: Tokenizes session summary text into sentences and strips unconsented categories (`ConsentFilterRequest` $\rightarrow$ `ConsentFilterResponse`).

### Handover & Continuity Endpoints
- **`POST /api/handovers/preview`**: Previews baseline vs prototype handover summaries, checks staff capacity, and calculates confidence score.
- **`POST /api/handovers/create`**: Commits handover record and allocates staff capacity or places on `Waitlisted`.
- **`POST /api/handovers/generate`**: Generates deterministic handover summary response (`HandoverGenerationRequest` $\rightarrow$ `HandoverSummaryResponse`).
- **`GET /api/handovers`**: Lists historical handover records.

### Section 10 Conflict Detection & Analytics Endpoints
- **`POST /api/conflict/detect`**: Executes Section 10 pairwise temporal session conflict scanning for contradictory statements (`ConflictCheckRequest` $\rightarrow$ `ConflictCheckResponse`).
- **`GET /api/evaluation/report`**: Runs empirical evaluation experiment comparing Naive Baseline vs Prototype.
- **`GET /api/dataset/summary`**: Returns synthetic dataset demographic and clinical status distributions.
- **`GET /api/audit-logs`**: Retrieves system audit trail logs (Requires RBAC authentication).

---

## 5. Technical Documentation on Unit Testing & Error Boundaries

For complete technical documentation on testing architecture, test isolation, and multi-layered error boundaries, see **[Granular Technical Documentation on Unit Testing & Error Boundaries](docs/testing_and_error_boundaries.md)**.

### Summary of Error Boundaries
1. **RBAC Boundary (Section 3)**: Administrators attempting to view raw session notes receive `HTTP 403 Forbidden` and log `FORBIDDEN` in audit trail.
2. **Safe Fallback Guardrail Boundary (Section 8 & 10)**: Summaries with confidence $< 0.60$ or Section 10 conflict flags display non-authoritative fallback warnings.
3. **Database Transaction Boundary**: Automatic ORM transaction rollback on exceptions.
4. **Staff Capacity Boundary**: Automatic waitlisting when destination staff `available_slots == 0`.
