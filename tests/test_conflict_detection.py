import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.handover.conflict_engine import detect_conflicts
from backend.handover.continuity_engine import generate_prototype_summary

def test_conflict_detection_relocation():
    sessions = [
        {"session_id": "S1", "session_date": "2026-08-01", "session_summary": "Client confirmed plan to relocate to overseas office."},
        {"session_id": "S2", "session_date": "2026-08-10", "session_summary": "Client states intention to remain on-site in local branch."}
    ]
    has_conflict, penalty, flags = detect_conflicts(sessions)
    assert has_conflict is True
    assert penalty == 0.40
    assert len(flags) > 0
    assert flags[0]["severity"] == "CRITICAL"
    assert flags[0]["conflict_category"] == "Employment Status"

def test_conflict_detection_substance():
    sessions = [
        {"session_id": "S1", "session_date": "2026-08-01", "session_summary": "Client reports sober lifestyle with no substance use."},
        {"session_id": "S2", "session_date": "2026-08-15", "session_summary": "Client experienced a severe substance relapse over weekend."}
    ]
    has_conflict, penalty, flags = detect_conflicts(sessions)
    assert has_conflict is True
    assert penalty == 0.40
    assert flags[0]["severity"] == "CRITICAL"

def test_no_conflict():
    sessions = [
        {"session_id": "S1", "session_date": "2026-08-01", "session_summary": "Client discussed workplace workload and anxiety."},
        {"session_id": "S2", "session_date": "2026-08-10", "session_summary": "Client reported good progress on mindfulness exercise."}
    ]
    has_conflict, penalty, flags = detect_conflicts(sessions)
    assert has_conflict is False
    assert penalty == 0.0
    assert len(flags) == 0
