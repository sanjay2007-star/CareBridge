import sys
import os
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import SessionLocal, engine, Base
from backend.models import Client, SessionRecord, ClientGoal, StaffUser, AuditLog, ConsentRecord
from backend.handover.continuity_engine import generate_prototype_summary
from backend.scheduling.scheduling_engine import check_and_allocate_staff_capacity

client = TestClient(app)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_case_3_conflicting_information(db_session):
    """Case 3: Conflicting Information -> Human review required."""
    c_id = "TEST_CONFLICT_01"
    db_session.add(Client(client_id=c_id, age_group="18-25", work_mode="Remote", preferred_language="English-primary", region="EMEA"))

    # Conflicting session text
    db_session.add(SessionRecord(
        session_id="SESS_CONF_1",
        client_id=c_id,
        counsellor_id="COUNS_001",
        session_date="2026-08-01",
        session_summary="Client confirmed plan to relocate to overseas office.",
        sensitivity_level="Medium"
    ))
    db_session.add(SessionRecord(
        session_id="SESS_CONF_2",
        client_id=c_id,
        counsellor_id="COUNS_001",
        session_date="2026-08-10",
        session_summary="Client states intention to remain on-site in local branch.",
        sensitivity_level="Medium"
    ))
    db_session.commit()

    summary_text, confidence, req_review, reasons, _, _ = generate_prototype_summary(db_session, c_id, "social_worker")
    assert req_review is True, "Conflicting info must trigger human review"
    assert "SAFE FALLBACK TRIGGERED" in summary_text
    assert any("Conflicting information" in r for r in reasons)

def test_case_4_low_confidence(db_session):
    """Case 4: Low Confidence -> Safe fallback displayed."""
    c_id = "TEST_LOWCONF_01"
    db_session.add(Client(client_id=c_id, age_group="51+", work_mode="On-site", preferred_language="English-primary", region="APAC"))
    # Old session > 60 days
    old_date = (datetime.utcnow() - timedelta(days=60)).strftime("%Y-%m-%d")
    db_session.add(SessionRecord(
        session_id="SESS_OLD_1",
        client_id=c_id,
        counsellor_id="COUNS_001",
        session_date=old_date,
        session_summary="Client mentioned workplace concerns long ago.",
        sensitivity_level="Low"
    ))
    db_session.commit()

    summary_text, confidence, req_review, reasons, _, _ = generate_prototype_summary(db_session, c_id, "social_worker")
    assert confidence < 0.60, "Old session and no active goals must lower confidence score below 0.60"
    assert "SAFE FALLBACK TRIGGERED" in summary_text

def test_case_5_staff_capacity_full(db_session):
    """Case 5: Staff Capacity Reached -> Case placed on WAITLIST."""
    staff_id = "SOC_BUSY_01"
    db_session.add(StaffUser(
        staff_id=staff_id,
        name="Busy Social Worker",
        role="social_worker",
        maximum_active_cases=5,
        current_active_cases=5,
        available_slots=0
    ))
    db_session.commit()

    available, msg, slots = check_and_allocate_staff_capacity(db_session, staff_id)
    assert available is False
    assert "WAITLIST" in msg

def test_case_6_unauthorised_access_audit(db_session):
    """Case 6: Unauthorised Access -> HTTP 403 & Audit event logged."""
    # Attempt admin endpoint call to raw session notes
    response = client.get(
        "/api/clients/C001/sessions",
        headers={"X-User-Id": "ADMIN_999", "X-User-Role": "admin"}
    )
    assert response.status_code == 403
    assert "Administrators do not have permission" in response.json()["detail"]

    # Verify audit log recorded forbidden attempt
    log = db_session.query(AuditLog).filter(AuditLog.user_id == "ADMIN_999").order_by(AuditLog.timestamp.desc()).first()
    assert log is not None
    assert log.result == "FORBIDDEN"
