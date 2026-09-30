from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ClientBase(BaseModel):
    client_id: str
    age_group: str
    work_mode: str
    preferred_language: str
    region: str

class ClientOut(ClientBase):
    created_at: datetime
    class Config:
        from_attributes = True

class StaffUserOut(BaseModel):
    staff_id: str
    name: str
    role: str
    specialisation: Optional[str] = None
    maximum_active_cases: int
    current_active_cases: int
    available_slots: int
    class Config:
        from_attributes = True

class SessionRecordOut(BaseModel):
    session_id: str
    client_id: str
    counsellor_id: str
    session_date: str
    session_summary: str
    sensitivity_level: str
    created_at: datetime
    class Config:
        from_attributes = True

class ClientGoalOut(BaseModel):
    goal_id: str
    client_id: str
    goal_category: str
    goal_description: str
    goal_status: str
    created_at: datetime
    class Config:
        from_attributes = True

class ConsentRecordOut(BaseModel):
    consent_id: str
    client_id: str
    information_category: str
    allowed_recipient_role: str
    consent_status: str
    granted_at: datetime
    revoked_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ConsentUpdate(BaseModel):
    client_id: str
    information_category: str
    allowed_recipient_role: str
    consent_status: str # granted or revoked

class PendingActionOut(BaseModel):
    action_id: str
    client_id: str
    assigned_role: str
    action_description: str
    priority: str
    due_date: str
    status: str
    class Config:
        from_attributes = True

class PendingActionCreate(BaseModel):
    client_id: str
    assigned_role: str
    action_description: str
    priority: str = "Medium"
    due_date: str

class HandoverCreate(BaseModel):
    client_id: str
    from_staff_id: str
    to_staff_id: str

class HandoverOut(BaseModel):
    handover_id: str
    client_id: str
    from_staff_id: str
    to_staff_id: str
    created_at: datetime
    handover_status: str
    confidence_score: float
    requires_human_review: bool
    baseline_summary: Optional[str] = None
    prototype_summary: Optional[str] = None
    class Config:
        from_attributes = True

class AuditLogOut(BaseModel):
    audit_id: str
    user_id: str
    client_id: Optional[str] = None
    action: str
    resource_type: str
    timestamp: datetime
    result: str
    class Config:
        from_attributes = True

class HandoverPreviewResponse(BaseModel):
    client_id: str
    from_staff_id: str
    to_staff_id: str
    recipient_role: str
    baseline_summary: str
    prototype_summary: str
    approved_categories: List[str]
    restricted_categories: List[str]
    confidence_score: float
    requires_human_review: bool
    review_reasons: List[str]
    privacy_validation_passed: bool
    staff_available: bool
    available_slots: int

class EvaluationReportResponse(BaseModel):
    total_handovers: int
    baseline_repetition_rate: float
    prototype_repetition_rate: float
    repetition_reduction: float
    consent_violation_rate: float
    summary_completeness: float
    pending_action_recall: float
    human_review_rate: float
    fairness_work_mode: dict
    fairness_language: dict

# Explicit Endpoint Schemas for Consent Engine & Handover Summary Generator & Conflict Detection
class ConsentCheckRequest(BaseModel):
    client_id: str
    information_category: str
    recipient_role: str

class ConsentCheckResponse(BaseModel):
    client_id: str
    information_category: str
    recipient_role: str
    is_consented: bool
    consent_status: str

class ConsentFilterRequest(BaseModel):
    client_id: str
    session_summary: str
    recipient_role: str

class ConsentFilterResponse(BaseModel):
    client_id: str
    recipient_role: str
    filtered_text: str
    approved_categories: List[str]
    restricted_categories: List[str]

class HandoverGenerationRequest(BaseModel):
    client_id: str
    from_staff_id: str
    to_staff_id: str

class HandoverSummaryResponse(BaseModel):
    client_id: str
    from_staff_id: str
    to_staff_id: str
    recipient_role: str
    baseline_summary: str
    prototype_summary: str
    confidence_score: float
    requires_human_review: bool
    review_reasons: List[str]
    approved_categories: List[str]
    restricted_categories: List[str]

class ConflictCheckRequest(BaseModel):
    client_id: str

class ConflictFlagOut(BaseModel):
    session_id_1: Optional[str] = None
    session_date_1: Optional[str] = None
    session_id_2: Optional[str] = None
    session_date_2: Optional[str] = None
    conflict_category: str
    severity: str
    description: str
    confidence_penalty: float

class ConflictCheckResponse(BaseModel):
    client_id: str
    has_conflict: bool
    max_confidence_penalty: float
    conflict_flags: List[ConflictFlagOut]

class SyntheticDatasetSummaryResponse(BaseModel):
    total_clients: int
    work_mode_distribution: dict
    language_distribution: dict
    age_group_distribution: dict
    total_sessions: int
    sensitivity_distribution: dict
    total_consents: int
    consent_status_distribution: dict
    staff_capacity: dict
    flagged_conflicts_count: int

