from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.models import Client, SessionRecord, ClientGoal, PendingAction, StaffUser
from backend.consent.consent_engine import filter_session_data, is_category_consented

def generate_baseline_summary(db: Session, client_id: str) -> str:
    """
    BASELINE HANDOVER (Section 9):
    Uses ONLY Client ID, Last session date, General goal, Pending action.
    Does NOT use intelligent continuity extraction or consent-aware filtering.
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
    PROTOTYPE HANDOVER SUMMARY (Sections 6, 7 & 8):
    Safe Processing Pipeline:
    Session Records -> Info Classification -> Consent Check -> Role Check -> Filter -> Safe Summary / Fallback.
    Returns: (summary_text, confidence_score, requires_human_review, review_reasons, approved_cats, restricted_cats)
    """
    sessions = db.query(SessionRecord).filter(SessionRecord.client_id == client_id).order_by(SessionRecord.session_date.desc()).all()
    goals = db.query(ClientGoal).filter(ClientGoal.client_id == client_id, ClientGoal.goal_status == "Active").all()
    actions = db.query(PendingAction).filter(PendingAction.client_id == client_id, PendingAction.status != "Completed").all()

    # 1. Filter Session Notes by Consent
    combined_approved_text = []
    all_approved_cats = set()
    all_restricted_cats = set()
    conflicting_info_detected = False

    # Check for contradictory session notes (Edge Case 3)
    summaries_text = " ".join([s.session_summary for s in sessions]).lower()
    if ("relocate" in summaries_text and "remain on-site" in summaries_text) or \
       ("full time" in summaries_text and "resigned" in summaries_text):
        conflicting_info_detected = True

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

    # 3. Pending Actions matching role
    relevant_actions = []
    for act in actions:
        if act.assigned_role.lower() == to_staff_role.lower() or to_staff_role.lower() == "admin":
            relevant_actions.append(f"- [{act.priority} Priority] {act.action_description} (Due: {act.due_date})")

    # 4. Confidence Score & Human Review Calculation
    confidence = 1.0
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
        confidence -= 0.30
        review_reasons.append("Conflicting information detected in session records.")

    if not approved_goals:
        confidence -= 0.15
        review_reasons.append("No active consent-approved goals found.")

    if not relevant_actions:
        confidence -= 0.15
        review_reasons.append("No pending actions assigned for this recipient role.")

    if len(all_restricted_cats) > 0:
        confidence -= 0.05
        review_reasons.append(f"Client restricted sharing for categories: {', '.join([c.replace('_', ' ') for c in all_restricted_cats])}.")

    confidence = round(max(0.0, min(1.0, confidence)), 2)

    requires_human_review = confidence < 0.60 or conflicting_info_detected

    # 5. Build Safe Summary OR Fallback Message
    if confidence < 0.60 or conflicting_info_detected:
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
