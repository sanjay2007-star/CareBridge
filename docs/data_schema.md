# Database Schema & API Endpoint Specifications

The database is built on SQLite with SQLAlchemy ORM models, complemented by FastAPI Pydantic request/response schemas.

---

## 1. Relational Database Entities

### CLIENT
- `client_id` (PK, String): Unique client identifier (e.g. C001)
- `age_group` (String): Demographic age group ('18-25', '26-35', '36-50', '51+')
- `work_mode` (String): 'Remote', 'Hybrid', 'On-site'
- `preferred_language` (String): 'English-primary', 'Multilingual/non-English-primary'
- `region` (String): Geographical region ('North America', 'EMEA', 'APAC', 'LATAM')
- `created_at` (DateTime): Registration timestamp

### SESSION
- `session_id` (PK, String): Unique session identifier (e.g. SESS_0001)
- `client_id` (FK, String): Client reference
- `counsellor_id` (FK, String): Counsellor reference
- `session_date` (String): Date formatted YYYY-MM-DD
- `session_summary` (Text): Raw confidential session notes
- `sensitivity_level` (String): 'Low', 'Medium', 'High'

### CONSENT
- `consent_id` (PK, String): Unique consent record identifier
- `client_id` (FK, String): Client reference
- `information_category` (String): 'workplace', 'financial', 'family', 'wellbeing', 'housing', 'legal_support'
- `allowed_recipient_role` (String): 'counsellor', 'social_worker', 'all'
- `consent_status` (String): 'granted', 'revoked'
- `granted_at` (DateTime): Consent grant timestamp
- `revoked_at` (DateTime, Nullable): Consent revocation timestamp

### CLIENT_GOAL
- `goal_id` (PK, String): Goal identifier
- `client_id` (FK, String): Client reference
- `goal_category` (String): Information category
- `goal_description` (Text): Structured goal statement
- `goal_status` (String): 'Active', 'Achieved', 'Paused'

### PENDING_ACTION
- `action_id` (PK, String): Action identifier
- `client_id` (FK, String): Client reference
- `assigned_role` (String): 'counsellor', 'social_worker'
- `action_description` (Text): Follow-up task description
- `priority` (String): 'High', 'Medium', 'Low'
- `due_date` (String): Target completion date
- `status` (String): 'Pending', 'In Progress', 'Completed'

### HANDOVER
- `handover_id` (PK, String): Handover record identifier
- `client_id` (FK, String): Client reference
- `from_staff_id` (FK, String): Source staff identifier
- `to_staff_id` (FK, String): Destination staff identifier
- `handover_status` (String): 'Approved', 'Human Review Required', 'Waitlisted'
- `confidence_score` (Float): Summary confidence rating (0.0 to 1.0)
- `requires_human_review` (Boolean): Guardrail flag
- `baseline_summary` (Text): Un-filtered naive baseline text
- `prototype_summary` (Text): Consent-filtered safe continuity output

### AUDIT_LOG
- `audit_id` (PK, String): Event identifier
- `user_id` (String): User performing action
- `client_id` (String, Nullable): Target client
- `action` (String): Audit event type
- `resource_type` (String): Entity type
- `timestamp` (DateTime): Event timestamp
- `result` (String): 'SUCCESS', 'FORBIDDEN'

### STAFF_CAPACITY
- `staff_id` (PK, String): Staff identifier
- `role` (String): 'counsellor', 'social_worker', 'admin'
- `maximum_active_cases` (Integer): Maximum workload cap
- `current_active_cases` (Integer): Active case load
- `available_slots` (Integer): Remaining open capacity

---

## 2. API Endpoint Schemas

### Consent Engine Endpoints
- `POST /api/consent/check`: Evaluates explicit client consent for a category & role (`ConsentCheckRequest` $\rightarrow$ `ConsentCheckResponse`).
- `POST /api/consent/filter`: Filters session summary text, returning approved vs restricted categories (`ConsentFilterRequest` $\rightarrow$ `ConsentFilterResponse`).

### Handover Generator Endpoints
- `POST /api/handovers/generate`: Generates deterministic baseline vs prototype handover summaries (`HandoverGenerationRequest` $\rightarrow$ `HandoverSummaryResponse`).
- `POST /api/handovers/preview`: Previews handover summary and checks staff capacity.

### Section 10 Conflict Detection Endpoint
- `POST /api/conflict/detect`: Runs Section 10 rule & semantic conflict detection across historical session notes (`ConflictCheckRequest` $\rightarrow$ `ConflictCheckResponse`).
