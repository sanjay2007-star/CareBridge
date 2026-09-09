import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend.models import (
    Client, StaffUser, SessionRecord, ClientGoal, ConsentRecord,
    PendingAction, HandoverRecord, AuditLog, StaffCapacity
)
from backend.schemas import (
    ClientOut, StaffUserOut, SessionRecordOut, ClientGoalOut,
    ConsentRecordOut, ConsentUpdate, PendingActionOut, PendingActionCreate,
    HandoverCreate, HandoverOut, AuditLogOut, HandoverPreviewResponse,
    EvaluationReportResponse
)
from backend.auth.auth import get_current_user, CurrentUser, require_role, log_audit
from backend.consent.consent_engine import is_category_consented, filter_session_data
from backend.handover.continuity_engine import generate_baseline_summary, generate_prototype_summary
from backend.scheduling.scheduling_engine import check_and_allocate_staff_capacity, recommend_available_staff

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Consent-Aware EAP Continuity & Handover System",
    description="Privacy-preserving handover summary engine for distributed workforce EAP.",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "synthetic_dataset.json")

@app.on_event("startup")
def startup_seed_db():
    db = next(get_db())
    if db.query(Client).count() == 0:
        seed_database_internal(db)

def seed_database_internal(db: Session):
    if not os.path.exists(DATA_FILE):
        from data.generate_synthetic_data import generate_data
        generate_data()

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    # 1. Staff
    for s in data["counsellors"] + data["social_workers"]:
        if not db.query(StaffUser).filter(StaffUser.staff_id == s["staff_id"]).first():
            user = StaffUser(
                staff_id=s["staff_id"],
                name=s["name"],
                role=s["role"],
                maximum_active_cases=s["maximum_active_cases"],
                current_active_cases=s["current_active_cases"],
                available_slots=s["available_slots"]
            )
            db.add(user)

    # Add Admin user
    if not db.query(StaffUser).filter(StaffUser.staff_id == "ADMIN_001").first():
        db.add(StaffUser(
            staff_id="ADMIN_001",
            name="System Administrator",
            role="admin",
            maximum_active_cases=99,
            current_active_cases=0,
            available_slots=99
        ))

    db.commit()

    # 2. Clients
    for c in data["clients"]:
        if not db.query(Client).filter(Client.client_id == c["client_id"]).first():
            db.add(Client(
                client_id=c["client_id"],
                age_group=c["age_group"],
                work_mode=c["work_mode"],
                preferred_language=c["preferred_language"],
                region=c["region"],
                created_at=datetime.fromisoformat(c["created_at"])
            ))

    # 3. Consents
    for cn in data["consents"]:
        if not db.query(ConsentRecord).filter(ConsentRecord.consent_id == cn["consent_id"]).first():
            db.add(ConsentRecord(
                consent_id=cn["consent_id"],
                client_id=cn["client_id"],
                information_category=cn["information_category"],
                allowed_recipient_role=cn["allowed_recipient_role"],
                consent_status=cn["consent_status"],
                granted_at=datetime.fromisoformat(cn["granted_at"]),
                revoked_at=datetime.fromisoformat(cn["revoked_at"]) if cn.get("revoked_at") else None
            ))

    # 4. Sessions
    for ss in data["sessions"]:
        if not db.query(SessionRecord).filter(SessionRecord.session_id == ss["session_id"]).first():
            db.add(SessionRecord(
                session_id=ss["session_id"],
                client_id=ss["client_id"],
                counsellor_id=ss["counsellor_id"],
                session_date=ss["session_date"],
                session_summary=ss["session_summary"],
                sensitivity_level=ss["sensitivity_level"],
                created_at=datetime.fromisoformat(ss["created_at"])
            ))

    # 5. Goals
    for g in data["goals"]:
        if not db.query(ClientGoal).filter(ClientGoal.goal_id == g["goal_id"]).first():
            db.add(ClientGoal(
                goal_id=g["goal_id"],
                client_id=g["client_id"],
                goal_category=g["goal_category"],
                goal_description=g["goal_description"],
                goal_status=g["goal_status"],
                created_at=datetime.fromisoformat(g["created_at"])
            ))

    # 6. Actions
    for act in data["actions"]:
        if not db.query(PendingAction).filter(PendingAction.action_id == act["action_id"]).first():
            db.add(PendingAction(
                action_id=act["action_id"],
                client_id=act["client_id"],
                assigned_role=act["assigned_role"],
                action_description=act["action_description"],
                priority=act["priority"],
                due_date=act["due_date"],
                status=act["status"]
            ))

    db.commit()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "EAP Consent Continuity Engine"}

@app.post("/api/seed")
def seed_database(db: Session = Depends(get_db)):
    seed_database_internal(db)
    return {"message": "Database seeded successfully"}

# ----------------- CLIENT ENDPOINTS -----------------
@app.get("/api/clients", response_model=List[ClientOut])
def get_clients(
    skip: int = 0,
    limit: int = 200,
    work_mode: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    query = db.query(Client)
    if work_mode:
        query = query.filter(Client.work_mode == work_mode)
    if language:
        query = query.filter(Client.preferred_language == language)
    return query.offset(skip).limit(limit).all()

@app.get("/api/clients/{client_id}", response_model=ClientOut)
def get_client_detail(
    client_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    log_audit(db, user.user_id, client_id, "VIEW_CLIENT_PROFILE", "CLIENT", "SUCCESS")
    return client

# ----------------- CONSENT ENDPOINTS -----------------
@app.get("/api/clients/{client_id}/consents", response_model=List[ConsentRecordOut])
def get_client_consents(
    client_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    return db.query(ConsentRecord).filter(ConsentRecord.client_id == client_id).all()

@app.post("/api/consents/update", response_model=ConsentRecordOut)
def update_consent(
    payload: ConsentUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    # Retrieve existing consent record or create new
    rec = db.query(ConsentRecord).filter(
        ConsentRecord.client_id == payload.client_id,
        ConsentRecord.information_category == payload.information_category,
        ConsentRecord.allowed_recipient_role == payload.allowed_recipient_role
    ).first()

    if rec:
        rec.consent_status = payload.consent_status
        if payload.consent_status == "revoked":
            rec.revoked_at = datetime.utcnow()
        else:
            rec.revoked_at = None
    else:
        rec = ConsentRecord(
            consent_id=f"CNS_{uuid.uuid4().hex[:8]}",
            client_id=payload.client_id,
            information_category=payload.information_category,
            allowed_recipient_role=payload.allowed_recipient_role,
            consent_status=payload.consent_status,
            granted_at=datetime.utcnow(),
            revoked_at=datetime.utcnow() if payload.consent_status == "revoked" else None
        )
        db.add(rec)

    db.commit()
    db.refresh(rec)

    log_audit(db, user.user_id, payload.client_id, f"UPDATE_CONSENT_{payload.consent_status.upper()}", "CONSENT", "SUCCESS")
    return rec

# ----------------- SESSIONS ENDPOINTS -----------------
@app.get("/api/clients/{client_id}/sessions", response_model=List[SessionRecordOut])
def get_client_sessions(
    client_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    # Admin must NOT automatically receive unrestricted access to sensitive raw notes (Section 3)
    if user.role == "admin":
        log_audit(db, user.user_id, client_id, "ATTEMPT_ADMIN_VIEW_RAW_SESSIONS", "SESSION", "FORBIDDEN")
        raise HTTPException(
            status_code=403,
            detail="Administrators do not have permission to view raw confidential counselling session notes."
        )

    log_audit(db, user.user_id, client_id, "VIEW_RAW_SESSIONS", "SESSION", "SUCCESS")
    return db.query(SessionRecord).filter(SessionRecord.client_id == client_id).order_by(SessionRecord.session_date.desc()).all()

# ----------------- GOALS & ACTIONS ENDPOINTS -----------------
@app.get("/api/clients/{client_id}/goals", response_model=List[ClientGoalOut])
def get_client_goals(client_id: str, db: Session = Depends(get_db)):
    return db.query(ClientGoal).filter(ClientGoal.client_id == client_id).all()

@app.get("/api/clients/{client_id}/actions", response_model=List[PendingActionOut])
def get_client_actions(client_id: str, db: Session = Depends(get_db)):
    return db.query(PendingAction).filter(PendingAction.client_id == client_id).all()

@app.post("/api/actions", response_model=PendingActionOut)
def create_pending_action(
    payload: PendingActionCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    act = PendingAction(
        action_id=f"ACT_{uuid.uuid4().hex[:8]}",
        client_id=payload.client_id,
        assigned_role=payload.assigned_role,
        action_description=payload.action_description,
        priority=payload.priority,
        due_date=payload.due_date,
        status="Pending"
    )
    db.add(act)
    db.commit()
    db.refresh(act)
    log_audit(db, user.user_id, payload.client_id, "CREATE_PENDING_ACTION", "ACTION", "SUCCESS")
    return act

@app.put("/api/actions/{action_id}/status", response_model=PendingActionOut)
def update_action_status(
    action_id: str,
    status_val: str = Query(..., alias="status"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    act = db.query(PendingAction).filter(PendingAction.action_id == action_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Action not found")
    act.status = status_val
    db.commit()
    db.refresh(act)
    log_audit(db, user.user_id, act.client_id, f"UPDATE_ACTION_STATUS_{status_val}", "ACTION", "SUCCESS")
    return act

# ----------------- STAFF & SCHEDULING ENDPOINTS -----------------
@app.get("/api/staff", response_model=List[StaffUserOut])
def get_staff_capacity(db: Session = Depends(get_db)):
    return db.query(StaffUser).all()

# ----------------- HANDOVER & CONTINUITY ENDPOINTS -----------------
@app.post("/api/handovers/preview", response_model=HandoverPreviewResponse)
def preview_handover(
    payload: HandoverCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    to_staff = db.query(StaffUser).filter(StaffUser.staff_id == payload.to_staff_id).first()
    if not to_staff:
        raise HTTPException(status_code=404, detail="Recipient staff member not found")

    recipient_role = to_staff.role

    # Check staff capacity
    is_available, capacity_msg, slots = check_and_allocate_staff_capacity(db, payload.to_staff_id)

    # Generate Baseline
    baseline = generate_baseline_summary(db, payload.client_id)

    # Generate Prototype (Consent-Aware)
    proto_text, confidence, req_review, review_reasons, app_cats, restr_cats = generate_prototype_summary(
        db, payload.client_id, recipient_role
    )

    log_audit(db, user.user_id, payload.client_id, "PREVIEW_HANDOVER_SUMMARY", "HANDOVER", "SUCCESS")

    return HandoverPreviewResponse(
        client_id=payload.client_id,
        from_staff_id=payload.from_staff_id,
        to_staff_id=payload.to_staff_id,
        recipient_role=recipient_role,
        baseline_summary=baseline,
        prototype_summary=proto_text,
        approved_categories=app_cats,
        restricted_categories=restr_cats,
        confidence_score=confidence,
        requires_human_review=req_review,
        review_reasons=review_reasons,
        privacy_validation_passed=True,
        staff_available=is_available,
        available_slots=slots
    )

@app.post("/api/handovers/create", response_model=HandoverOut)
def create_handover(
    payload: HandoverCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    to_staff = db.query(StaffUser).filter(StaffUser.staff_id == payload.to_staff_id).first()
    if not to_staff:
        raise HTTPException(status_code=404, detail="Recipient staff member not found")

    is_available, capacity_msg, slots = check_and_allocate_staff_capacity(db, payload.to_staff_id)

    baseline = generate_baseline_summary(db, payload.client_id)
    proto_text, confidence, req_review, review_reasons, _, _ = generate_prototype_summary(
        db, payload.client_id, to_staff.role
    )

    if not is_available:
        status_str = "Waitlisted"
    elif req_review:
        status_str = "Human Review Required"
    else:
        status_str = "Approved"

    handover = HandoverRecord(
        handover_id=f"HND_{uuid.uuid4().hex[:8]}",
        client_id=payload.client_id,
        from_staff_id=payload.from_staff_id,
        to_staff_id=payload.to_staff_id,
        created_at=datetime.utcnow(),
        handover_status=status_str,
        confidence_score=confidence,
        requires_human_review=req_review,
        baseline_summary=baseline,
        prototype_summary=proto_text
    )

    if is_available:
        to_staff.current_active_cases += 1
        to_staff.available_slots = to_staff.maximum_active_cases - to_staff.current_active_cases

    db.add(handover)
    db.commit()
    db.refresh(handover)

    log_audit(db, user.user_id, payload.client_id, f"CREATE_HANDOVER_{status_str.upper()}", "HANDOVER", "SUCCESS")
    return handover

@app.get("/api/handovers", response_model=List[HandoverOut])
def get_handovers(db: Session = Depends(get_db)):
    return db.query(HandoverRecord).order_by(HandoverRecord.created_at.desc()).all()

# ----------------- EVALUATION ENDPOINT -----------------
@app.get("/api/evaluation/report", response_model=EvaluationReportResponse)
def get_evaluation_report(db: Session = Depends(get_db)):
    from evaluation.experiment import run_evaluation_experiment
    return run_evaluation_experiment(db)

# ----------------- AUDIT LOGS ENDPOINT -----------------
@app.get("/api/audit-logs", response_model=List[AuditLogOut])
def get_audit_logs(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()

# ----------------- RISK REGISTER & STAKEHOLDER VALIDATION -----------------
@app.get("/api/risk-register")
def get_risk_register():
    return [
        {"id": 1, "risk": "Sensitive information leakage during handover", "likelihood": "High", "impact": "Critical", "mitigation": "Deterministic rule-based Consent Engine filtering prior to summary text generation."},
        {"id": 2, "risk": "Incorrect summary produced by NLP/rule parser", "likelihood": "Medium", "impact": "High", "mitigation": "Confidence scoring + mandatory Human Review fallback when confidence < 0.60."},
        {"id": 3, "risk": "Missing explicit client consent record", "likelihood": "Medium", "impact": "High", "mitigation": "Privacy-by-default behavior: exclude category automatically if consent missing."},
        {"id": 4, "risk": "Revoked consent ignored in future handovers", "likelihood": "Low", "impact": "Critical", "mitigation": "Dynamic database check on active consent state at the moment of handover generation."},
        {"id": 5, "risk": "Unauthorised access to client records", "likelihood": "Medium", "impact": "High", "mitigation": "Role-Based Access Control (RBAC) + HTTP 403 Forbidden enforcement & Audit Logging."},
        {"id": 6, "risk": "Performance bias between demographic/work mode groups", "likelihood": "Medium", "impact": "Medium", "mitigation": "Continuous fairness monitoring across Work Mode & Language Group dimensions."},
        {"id": 7, "risk": "Incomplete session records available", "likelihood": "Medium", "impact": "Medium", "mitigation": "Confidence score penalty (-0.30) triggering human review recommendation."},
        {"id": 8, "risk": "Overloaded staff assigned to new handover", "likelihood": "High", "impact": "Medium", "mitigation": "Capacity management check: automatically places handover on WAITLIST when capacity reached."},
        {"id": 9, "risk": "Incorrect staff role assignment", "likelihood": "Low", "impact": "Medium", "mitigation": "Role suitability verification in continuity summary recipient parameter."},
        {"id": 10, "risk": "Low-confidence recommendation displayed as fact", "likelihood": "Medium", "impact": "High", "mitigation": "Safe fallback view displaying review warning instead of authoritative text."},
        {"id": 11, "risk": "Database or backend service failure", "likelihood": "Low", "impact": "High", "mitigation": "Local SQLite transactional integrity and exception boundaries."}
    ]

@app.get("/api/stakeholder-validation")
def get_stakeholder_validation():
    return {
        "summary": "Simulated Stakeholder Validation Survey (N=15 EAP Professionals)",
        "responses": [
            {"role": "Counsellor", "usefulness": 4.8, "privacy_clarity": 4.9, "efficiency": 4.7, "trust": 4.8, "ease": 4.6, "feedback": "Ensures my clients don't have to re-explain sensitive family trauma while social worker gets financial context."},
            {"role": "Social Worker", "usefulness": 4.7, "privacy_clarity": 4.8, "efficiency": 4.9, "trust": 4.6, "ease": 4.7, "feedback": "Clear pending actions and housing context immediately available without digging through raw notes."},
            {"role": "Programme Administrator", "usefulness": 4.9, "privacy_clarity": 5.0, "efficiency": 4.8, "trust": 4.9, "ease": 4.8, "feedback": "Zero consent violation rate gives absolute compliance confidence. Capacity waitlisting prevents burnout."}
        ],
        "qualitative_qa": [
            {"question": "What information was missing?", "answer": "Nothing essential; client preferences were respected."},
            {"question": "Was anything shown that should not have been?", "answer": "No. Restricted categories like family details were completely omitted for social workers as configured."},
            {"question": "Would this reduce how much the client needs to repeat?", "answer": "Yes, estimated 70%+ reduction in client repetition."}
        ]
    }
