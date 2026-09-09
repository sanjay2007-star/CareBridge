from sqlalchemy.orm import Session
from backend.handover.continuity_engine import generate_baseline_summary

def run_baseline_for_client(db: Session, client_id: str) -> str:
    return generate_baseline_summary(db, client_id)
