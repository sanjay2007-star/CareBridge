from typing import List, Dict

def calculate_repetition_rate(repeated_facts: int, total_facts: int) -> float:
    if total_facts == 0:
        return 0.0
    return round(repeated_facts / total_facts, 4)

def calculate_repetition_reduction(baseline_rep: float, proto_rep: float) -> float:
    if baseline_rep == 0:
        return 0.0
    reduction = ((baseline_rep - proto_rep) / baseline_rep) * 100.0
    return round(max(0.0, reduction), 2)

def calculate_consent_violation_rate(exposed_restricted_facts: int, total_restricted_facts: int) -> float:
    if total_restricted_facts == 0:
        return 0.0
    return round((exposed_restricted_facts / total_restricted_facts) * 100.0, 2)

def calculate_completeness(included_approved_facts: int, total_approved_facts: int) -> float:
    if total_approved_facts == 0:
        return 1.0
    return round((included_approved_facts / total_approved_facts) * 100.0, 2)

def calculate_pending_action_recall(included_actions: int, total_required_actions: int) -> float:
    if total_required_actions == 0:
        return 1.0
    return round((included_actions / total_required_actions) * 100.0, 2)

def calculate_human_review_rate(review_cases: int, total_handovers: int) -> float:
    if total_handovers == 0:
        return 0.0
    return round((review_cases / total_handovers) * 100.0, 2)
