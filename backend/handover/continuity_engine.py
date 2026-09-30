"""
Continuity Engine Module
========================
Generates baseline vs prototype consent-aware handover summaries, calculates confidence scores,
and enforces Safe Fallback Guardrails when confidence falls below threshold (< 0.60) or when
Section 10 conflicts are detected.

Processing Pipeline:
1. Query Client Records (Sessions, Active Goals, Role-Matched Pending Actions).
2. Execute Deterministic Consent Filter on session notes & goals.
3. Execute Section 10 Conflict Detection Scan.
4. Compute Confidence Score & Safe Fallback Thresholds.
5. Format Authoritative Continuity Summary OR Safe Fallback Notice.
"""

from typing import Dict, List, Tuple, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.models import Client, SessionRecord, ClientGoal, PendingAction, StaffUser
from backend.consent.consent_engine import filter_session_data, is_category_consented
from backend.handover.conflict_engine import detect_conflicts

def generate_baseline_summary(db: Session, client_id: str) -> str:
    """
    BASELINE HANDOVER GENERATOR (Section 9 Benchmark):
    Produces a naive, unfiltered summary containing raw notes, un-scoped goals, and single pending actions.
    Used exclusively as an empirical benchmark to measure Repetition Reduction and Privacy Violation leakage.

    Args:
        db (Session): Database session context.
        client_id (str): Target client ID.

    Returns:
        str: Unfiltered baseline handover text.
    """
    sessions = db.query(SessionRecord).filter(SessionRecord.client_id == client_id).order_by(SessionRecord.session_date.desc()).all()
    goals = db.query(ClientGoal).filter(ClientGoal.client_id == client_id).all()
    actions = db.query(PendingAction).filter(PendingAction.client_id == client_id).all()

    last_session_date = sessions[0].session_date if sessions else "N/A"
    last_session_raw = sessions[0].session_summary if sessions else "No prior session recorded."
    first_goal = goals[0].goal_description if goals else "No goal specified."
    first_action = actions[0].action_description if actions else "No pending action."

    baseline_text = f"""[BASELINE HANDOVER SUMMARY]
Client ID: {client_id}
Last Session Date: {last_session_date}
Raw Last Session Summary: {last_session_raw}
General Goal: {first_goal}
Pending Action: {first_action}
Notice: Baseline summary un-filtered for consent categories.
"""
    return baseline_text

def generate_prototype_summary(db: Session, client_id: str, to_staff_role: str) -> Tuple[str, float, bool, List[str], List[str], List[str]]:
    """
    PROTOTYPE CONSENT-AWARE HANDOVER SUMMARY GENERATOR (Sections 6, 7, 8 & 10):
    Executes the complete safe processing pipeline:
    Session Records -> Info Classification -> Consent Check -> Role Check -> Section 10 Conflict Check -> Safe Summary / Fallback.

    Confidence Scoring Formula:
    - Base Score = 1.00
    - Missing sessions: -0.30
    - Outdated sessions (> 45 days old): -0.20
    - Section 10 Conflicts detected: -(conflict_penalty) [0.15 to 0.40]
    - No consent-approved goals: -0.15
    - No role-matched pending actions: -0.15
    - Client category restrictions present: -0.05

    Safe Fallback Trigger:
    Triggered IF confidence < 0.60 OR conflicting_info_detected == True.

    Args:
        db (Session): Database session context.
        client_id (str): Client ID receiving handover.
        to_staff_role (str): Role of receiving staff member ('counsellor', 'social_worker').

    Returns:
        Tuple[str, float, bool, List[str], List[str], List[str]]:
            - summary_text (str): Safe formatted continuity text or Safe Fallback notice.
            - confidence_score (float): Calculated rating between 0.00 and 1.00.
            - requires_human_review (bool): True if confidence < 0.60 or conflict flagged.
            - review_reasons (List[str]): List of warning flags or reasons.
            - approved_categories (List[str]): List of categories approved and included.
            - restricted_categories (List[str]): List of categories omitted due to privacy settings.
    """
    sessions = db.query(SessionRecord).filter(SessionRecord.client_id == client_id).order_by(SessionRecord.session_date.desc()).all()
    goals = db.query(ClientGoal).filter(ClientGoal.client_id == client_id, ClientGoal.goal_status == "Active").all()
    actions = db.query(PendingAction).filter(PendingAction.client_id == client_id, PendingAction.status != "Completed").all()

    # 1. Filter Session Notes by Consent
    combined_approved_text = []
    all_approved_cats = set()
    all_restricted_cats = set()

    # Section 10 Conflict Detection Scan
    session_dicts = [
        {"session_id": s.session_id, "session_date": s.session_date, "session_summary": s.session_summary}
        for s in sessions
    ]
    conflicting_info_detected, conflict_penalty, conflict_flags = detect_conflicts(session_dicts)

    for sess in sessions:
        filtered_text, app_cats, restr_cats = filter_session_data(db, client_id, sess.session_summary, to_staff_role)
        if filtered_text:
            combined_approved_text.append(f"[{sess.session_date}]: {filtered_text}")
        all_approved_cats.update(app_cats)
        all_restricted_cats.update(restr_cats)

    # 2. Filter Goals by Consent
    approved_goals = []
    for g in goals:
        if is_category_consented(db, client_id, g.goal_category, to_staff_role):
            approved_goals.append(f"- {g.goal_description} ({g.goal_category.replace('_', ' ').title()})")
        else:
            all_restricted_cats.add(g.goal_category)

    # 3. Pending Actions matching recipient role
    relevant_actions = []
    for act in actions:
        if act.assigned_role.lower() == to_staff_role.lower() or to_staff_role.lower() == "admin":
            relevant_actions.append(f"- [{act.priority} Priority] {act.action_description} (Due: {act.due_date})")

    # 4. Confidence Score & Human Review Calculation
    confidence = 1.00
    review_reasons = []

    if not sessions:
        confidence -= 0.30
        review_reasons.append("No historical session records found.")
    else:
        latest_date = datetime.strptime(sessions[0].session_date, "%Y-%m-%d")
        if (datetime.utcnow() - latest_date).days > 45:
            confidence -= 0.20
            review_reasons.append("Most recent session is older than 45 days.")

    if conflicting_info_detected:
        confidence -= (conflict_penalty if conflict_penalty > 0 else 0.30)
        details_str = "; ".join([f"{f['conflict_category']} ({f['severity']}): {f['description']}" for f in conflict_flags]) if conflict_flags else "Conflicting information detected."
        review_reasons.append(f"Conflicting information detected in session records: {details_str}")

    if not approved_goals:
        confidence -= 0.15
        review_reasons.append("No active consent-approved goals found.")

    if not relevant_actions:
        confidence -= 0.15
        review_reasons.append("No pending actions assigned for this recipient role.")

    if len(all_restricted_cats) > 0:
        confidence -= 0.05
        review_reasons.append(f"Client restricted sharing for categories: {', '.join([c.replace('_', ' ') for c in all_restricted_cats])}.")

    confidence = round(max(0.00, min(1.00, confidence)), 2)
    requires_human_review = confidence < 0.60 or conflicting_info_detected

    # 5. Build Safe Summary OR Safe Fallback Message
    if requires_human_review:
        summary_text = (
            "⚠️ SAFE FALLBACK TRIGGERED\n"
            "Insufficient verified information for a safe continuity summary. "
            "Please review the available records and confirm relevant information directly with the client.\n\n"
            f"Review Reasons: {'; '.join(review_reasons)}"
        )
    else:
        context_str = "\n".join(combined_approved_text[:3]) if combined_approved_text else "No recent consent-approved session notes."
        goals_str = "\n".join(approved_goals) if approved_goals else "No active consent-approved goals."
        actions_str = "\n".join(relevant_actions) if relevant_actions else "No active pending actions for recipient role."

        summary_text = f"""Structured Continuity Summary for Client {client_id}
Target Recipient Role: {to_staff_role.replace('_', ' ').title()}
Handover Reason: Inter-professional transfer for ongoing EAP support

1. Current Consent-Approved Goals:
{goals_str}

2. Approved Clinical & Support Context:
{context_str}

3. Pending Handover Actions:
{actions_str}

4. Important Follow-up Items:
- Verify client comfort with new primary care provider
- Confirm ongoing consent status during next session
"""

    return summary_text, confidence, requires_human_review, review_reasons, list(all_approved_cats), list(all_restricted_cats)
