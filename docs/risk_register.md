# System Risk Register & Mitigation Matrix

| ID | Risk Description | Likelihood | Impact | System Safeguard / Mitigation |
|---|---|---|---|---|
| 1 | Sensitive information leakage during handover | High | Critical | Deterministic rule-based Consent Engine filtering prior to summary text generation. |
| 2 | Incorrect summary produced by NLP parser | Medium | High | Confidence scoring + mandatory Human Review fallback when confidence < 0.60. |
| 3 | Missing explicit client consent record | Medium | High | Privacy-by-default behavior: exclude category automatically if consent missing. |
| 4 | Revoked consent ignored in future handovers | Low | Critical | Dynamic database check on active consent state at the moment of handover generation. |
| 5 | Unauthorised access to client records | Medium | High | Role-Based Access Control (RBAC) + HTTP 403 Forbidden enforcement & Audit Logging. |
| 6 | Performance bias between demographic groups | Medium | Medium | Continuous fairness monitoring across Work Mode & Language Group dimensions. |
| 7 | Incomplete session records available | Medium | Medium | Confidence score penalty (-0.30) triggering human review recommendation. |
| 8 | Overloaded staff assigned to new handover | High | Medium | Capacity management check: automatically places handover on WAITLIST when capacity reached. |
| 9 | Incorrect staff role assignment | Low | Medium | Role suitability verification in continuity summary recipient parameter. |
| 10 | Low-confidence recommendation displayed as fact | Medium | High | Safe fallback view displaying review warning instead of authoritative text. |
| 11 | Database or backend service failure | Low | High | Local SQLite transactional integrity and exception boundaries. |
