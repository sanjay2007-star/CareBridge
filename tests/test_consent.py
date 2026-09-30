import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Base, Client, ConsentRecord, SessionRecord, ClientGoal, StaffUser
from backend.consent.consent_engine import is_category_consented, filter_session_data

TEST_DB_FILE = os.path.join(os.path.dirname(__file__), "test_consent_temp.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

@pytest.fixture(scope="function")
def db_session(setup_test_db):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=setup_test_db)
    db = TestingSessionLocal()
    yield db
    db.close()

def test_missing_consent_excludes_information(db_session):
    """Case 1: Missing Consent -> Information excluded by default."""
    client_id = "TEST_NOCONSENT_01"
    c = Client(client_id=client_id, age_group="26-35", work_mode="Remote", preferred_language="English-primary", region="EMEA")
    db_session.add(c)
    db_session.commit()

    is_granted = is_category_consented(db_session, client_id, "financial", "social_worker")
    assert is_granted is False, "Missing consent should evaluate to False (privacy-by-default)"

    session_text = "Client shared financial difficulty and housing stress."
    filtered, approved_cats, restr_cats = filter_session_data(db_session, client_id, session_text, "social_worker")
    assert filtered == "", "Filtered text should be empty when consent is missing"
    assert "financial" in restr_cats

def test_revoked_consent_excludes_information(db_session):
    """Case 2: Revoked Consent -> Excluded from future handovers."""
    client_id = "TEST_REVOKED_01"
    c = Client(client_id=client_id, age_group="36-50", work_mode="Hybrid", preferred_language="English-primary", region="North America")
    db_session.add(c)

    cn = ConsentRecord(
        consent_id="CNS_REV_1",
        client_id=client_id,
        information_category="family",
        allowed_recipient_role="social_worker",
        consent_status="revoked",
        revoked_at=os.sys.modules['datetime'].datetime.utcnow()
    )
    db_session.add(cn)
    db_session.commit()

    is_granted = is_category_consented(db_session, client_id, "family", "social_worker")
    assert is_granted is False, "Revoked consent must return False"
