# Granular Technical Documentation: Unit Testing & Error Boundaries

This document provides a detailed technical specification of the **Unit Testing Architecture**, **Database Test Isolation Strategy**, and **Multi-Layered Error Boundaries** implemented in the **Consent-Aware EAP Continuity & Handover System**.

---

## 1. Unit & Integration Testing Architecture

The automated test suite is powered by `pytest` and `httpx` / FastAPI `TestClient`, enforcing high coverage across privacy rules, failure guardrails, role access control, capacity bounds, and clinical conflict detection.

```
                  +-----------------------------------+
                  |         pytest Test Runner         |
                  +-----------------------------------+
                                    |
       +----------------------------+----------------------------+
       |                            |                            |
[ test_consent.py ]        [ test_failures.py ]      [ test_conflict_detection.py ]
  - Privacy-by-Default      - Conflicting Notes        - Opposing Keywords
  - Missing Consent         - Low Confidence Threshold - Section 10 Penalty Scenarios
  - Revoked Consent State   - Staff Capacity Waitlist  - Sovereign Case Matrix
                            - RBAC HTTP 403 Forbidden
```

### A. Test Suite Breakdown

| Test File | Target Module | Scope & Objective | Failure Scenarios Tested |
|---|---|---|---|
| [`tests/test_consent.py`](file:///c:/Users/Sanjay%20v/Downloads/COE_project/tests/test_consent.py) | Consent Engine | Verifies deterministic filtering rules, category keyword matching, and recipient role constraints. | 1. **Missing Consent Record**: Evaluates to `False` by default (privacy-by-default).<br>2. **Revoked Consent**: Ensures revoked status (`consent_status == "revoked"`) strips topic text from handover output. |
| [`tests/test_failures.py`](file:///c:/Users/Sanjay%20v/Downloads/COE_project/tests/test_failures.py) | Continuity Engine & RBAC | Evaluates system guardrails, confidence threshold penalties, staff capacity waitlisting, and RBAC authorization boundaries. | 3. **Conflicting Session Notes**: Triggers `requires_human_review = True` and displays `⚠️ SAFE FALLBACK TRIGGERED`.<br>4. **Low Confidence Score**: Outdated notes ($>45$ days) lower score $< 0.60$, triggering safe fallback.<br>5. **Full Staff Capacity**: Assigning handovers to overloaded staff places record on `WAITLIST`.<br>6. **Admin Raw Access Attempt**: Administrators attempting to view raw session notes receive `HTTP 403 Forbidden` and log audit failure. |
| [`tests/test_conflict_detection.py`](file:///c:/Users/Sanjay%20v/Downloads/COE_project/tests/test_conflict_detection.py) | Section 10 Conflict Engine | Validates pairwise temporal session scanning for opposing clinical/operational statements. | 7. **Relocation Conflict**: Relocate vs remain on-site ($0.40$ penalty).<br>8. **Substance Misuse Conflict**: Sober reporting vs active relapse ($0.40$ penalty).<br>9. **Normal Progress Check**: Non-conflicting notes maintain $1.00$ base confidence. |

---

### B. Database Test Isolation Strategy

To prevent state pollution, deadlocks, or `UNIQUE constraint failed` errors when running tests against an active production database (`data/eap_continuity.db`), test execution uses **File-Based Temporary Test Databases with Isolated Lifecycles**:

1. **Explicit Isolation**: Each test module initializes a temporary SQLite database file (e.g. `test_failures_temp.db`).
2. **Schema Pre-Initialization**: `Base.metadata.create_all(bind=test_engine)` is invoked *after* importing all ORM models (`Client`, `SessionRecord`, `ConsentRecord`, `ClientGoal`, `PendingAction`, `HandoverRecord`, `AuditLog`, `StaffCapacity`).
3. **FastAPI Dependency Override**: Replaces `get_db` with `override_get_db()` yielding scoped session connections to `test_engine`:
   ```python
   app.dependency_overrides[get_db] = override_get_db
   ```
4. **Automated Teardown**: Fixtures delete temporary DB files upon suite completion.

---

## 2. Multi-Layered Error Boundaries Architecture

The application implements defense-in-depth error boundaries across all system layers to prevent raw exception leakage, unauthorized data access, or erroneous automated summary displays.

```
[ Layer 1: HTTP API Request Boundary ]
   ├── FastAPI Exception Handling Middleware (HTTP 400, 403, 404, 422)
   └── Dynamic CORS & Header Authorization Filters

[ Layer 2: Role-Based Access Control (RBAC) Boundary ]
   ├── Staff Role Verification (counsellor vs social_worker vs admin)
   └── Immutable Audit Logging (`log_audit()` records SUCCESS / FORBIDDEN)

[ Layer 3: Privacy & Consent Filtering Boundary ]
   ├── Privacy-by-Default Fallback (Missing record -> False)
   └── Sentence-Level Punctuation Tokenizer & Stripper

[ Layer 4: Clinical Conflict & Confidence Guardrail Boundary ]
   ├── Section 10 Conflict Detection Scan (-0.15 to -0.40 score penalty)
   └── Safe Fallback Message View (Triggered if Confidence < 0.60 or Conflict Flagged)

[ Layer 5: Database & Capacity Boundary ]
   ├── SQLAlchemy Transaction Boundaries (`db.rollback()` on error)
   └── Automatic Overflow Staff Waitlisting (`available_slots == 0`)
```

---

### Granular Error Boundary Specifications

#### 1. RBAC Privacy Access Boundary (Section 3 & HTTP 403)
- **Rule**: System administrators possess administrative privileges for capacity & user management, but are strictly prohibited from viewing confidential raw counselling session notes.
- **Enforcement**:
  ```python
  if user.role == "admin":
      log_audit(db, user.user_id, client_id, "ATTEMPT_ADMIN_VIEW_RAW_SESSIONS", "SESSION", "FORBIDDEN")
      raise HTTPException(
          status_code=403,
          detail="Administrators do not have permission to view raw confidential counselling session notes."
      )
  ```
- **Audit Logging**: Every unauthorized access attempt is immutably logged to `audit_logs` with result `FORBIDDEN`.

---

#### 2. Clinical Confidence & Safe Fallback Guardrail Boundary (Section 8 & 10)
- **Rule**: Automated summary text must never present incomplete, outdated ($> 45$ days), unverified, or contradictory information as authoritative clinical fact.
- **Threshold**:
  $$\text{Safe Fallback Triggered} \iff (\text{Confidence Score} < 0.60) \lor (\text{Section 10 Conflict Flagged} = \text{True})$$
- **Output Shift**: Replaces standard structured text with a clear warning:
  ```
  ⚠️ SAFE FALLBACK TRIGGERED
  Insufficient verified information for a safe continuity summary.
  Please review the available records and confirm relevant information directly with the client.
  
  Review Reasons: Conflicting information detected in session records: Employment Status (CRITICAL): Contradictory relocation vs local retention plans across sessions.
  ```

---

#### 3. Database Transaction & Staff Capacity Boundaries (Section 4)
- **Capacity Overflow Boundary**: When a destination staff member's `available_slots <= 0`, handovers are automatically marked as `handover_status = "Waitlisted"`, preserving workload safety.
- **DB Integrity Boundary**: Transactions use explicit SQLAlchemy ORM session scoping with automatic rollback on DB errors to preserve database state.
