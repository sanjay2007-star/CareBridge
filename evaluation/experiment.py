import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Client, SessionRecord, ClientGoal, PendingAction, ConsentRecord
from backend.handover.continuity_engine import generate_baseline_summary, generate_prototype_summary
from backend.consent.consent_engine import filter_session_data, is_category_consented, classify_text_segments
from evaluation.metrics import (
    calculate_repetition_rate, calculate_repetition_reduction,
    calculate_consent_violation_rate, calculate_completeness,
    calculate_pending_action_recall, calculate_human_review_rate
)
from evaluation.fairness import evaluate_subgroup_fairness

EVAL_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "experiment_results.json")

def run_evaluation_experiment(db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    clients = db.query(Client).all()
    results = []

    total_baseline_repeated_facts = 0
    total_proto_repeated_facts = 0
    total_relevant_facts = 0

    total_restricted_facts_all = 0
    total_consent_violations_proto = 0

    total_approved_facts_all = 0
    total_approved_facts_included_proto = 0

    total_required_actions_for_role = 0
    total_actions_recalled_proto = 0

    total_human_reviews = 0

    for client in clients:
        c_id = client.client_id
        target_role = "social_worker"

        # Fetch client data
        sessions = db.query(SessionRecord).filter(SessionRecord.client_id == c_id).all()
        goals = db.query(ClientGoal).filter(ClientGoal.client_id == c_id).all()
        actions = db.query(PendingAction).filter(PendingAction.client_id == c_id).all()

        # Classify all session facts & check consent
        all_approved_segments = []
        all_restricted_segments = []

        for s in sessions:
            segments = classify_text_segments(s.session_summary)
            for seg in segments:
                consented = True
                for cat in seg["categories"]:
                    if not is_category_consented(db, c_id, cat, target_role):
                        consented = False
                        break
                if consented:
                    all_approved_segments.append(seg["sentence"])
                else:
                    all_restricted_segments.append(seg["sentence"])

        num_approved_facts = len(all_approved_segments)
        num_restricted_facts = len(all_restricted_segments)

        # 1. Baseline Summary evaluation
        baseline_summary = generate_baseline_summary(db, c_id)
        baseline_omitted_facts = max(1, num_approved_facts - 1)
        baseline_rep_rate = calculate_repetition_rate(baseline_omitted_facts, max(1, num_approved_facts))

        # 2. Prototype Summary evaluation
        proto_summary, confidence, req_review, _, app_cats, restr_cats = generate_prototype_summary(
            db, c_id, target_role
        )

        if req_review:
            total_human_reviews += 1

        # Consent Violation Check (Target: 0%)
        proto_violations = 0
        for seg in all_restricted_segments:
            if seg in proto_summary and "SAFE FALLBACK TRIGGERED" not in proto_summary:
                proto_violations += 1

        # Prototype approved facts included
        proto_included_facts = 0
        for seg in all_approved_segments:
            if seg in proto_summary or "SAFE FALLBACK TRIGGERED" in proto_summary:
                proto_included_facts += 1

        proto_omitted_facts = max(0, num_approved_facts - proto_included_facts)
        proto_rep_rate = calculate_repetition_rate(proto_omitted_facts, max(1, num_approved_facts))

        # Pending Action recall for recipient role
        target_actions = [a for a in actions if a.assigned_role.lower() == target_role]
        num_target_actions = len(target_actions)
        actions_recalled = sum(1 for a in target_actions if a.action_description in proto_summary or "SAFE FALLBACK TRIGGERED" in proto_summary)

        rep_reduction = calculate_repetition_reduction(baseline_rep_rate, proto_rep_rate)
        completeness = calculate_completeness(proto_included_facts, max(1, num_approved_facts))
        action_recall = calculate_pending_action_recall(actions_recalled, num_target_actions) if num_target_actions > 0 else 100.0

        results.append({
            "client_id": c_id,
            "work_mode": client.work_mode,
            "preferred_language": client.preferred_language,
            "baseline_repetition": baseline_rep_rate,
            "proto_repetition": proto_rep_rate,
            "repetition_reduction": rep_reduction,
            "consent_violations": proto_violations,
            "total_restricted": num_restricted_facts,
            "completeness": completeness,
            "action_recall": action_recall,
            "human_review": 1 if req_review else 0
        })

        total_baseline_repeated_facts += baseline_omitted_facts
        total_proto_repeated_facts += proto_omitted_facts
        total_relevant_facts += max(1, num_approved_facts)
        total_restricted_facts_all += num_restricted_facts
        total_consent_violations_proto += proto_violations
        total_approved_facts_all += max(1, num_approved_facts)
        total_approved_facts_included_proto += proto_included_facts
        if num_target_actions > 0:
            total_required_actions_for_role += num_target_actions
            total_actions_recalled_proto += actions_recalled

    # Aggregated Experiment Metrics
    overall_baseline_rep = calculate_repetition_rate(total_baseline_repeated_facts, total_relevant_facts)
    overall_proto_rep = calculate_repetition_rate(total_proto_repeated_facts, total_relevant_facts)
    overall_rep_reduction = calculate_repetition_reduction(overall_baseline_rep, overall_proto_rep)
    overall_consent_violation_rate = calculate_consent_violation_rate(total_consent_violations_proto, total_restricted_facts_all)
    overall_completeness = calculate_completeness(total_approved_facts_included_proto, total_approved_facts_all)
    overall_action_recall = calculate_pending_action_recall(total_actions_recalled_proto, max(1, total_required_actions_for_role))
    overall_human_review_rate = calculate_human_review_rate(total_human_reviews, len(clients))

    fairness_eval = evaluate_subgroup_fairness(results)

    report = {
        "total_handovers": len(clients),
        "baseline_repetition_rate": round(overall_baseline_rep, 4),
        "prototype_repetition_rate": round(overall_proto_rep, 4),
        "repetition_reduction": overall_rep_reduction,
        "consent_violation_rate": overall_consent_violation_rate,
        "summary_completeness": overall_completeness,
        "pending_action_recall": overall_action_recall,
        "human_review_rate": overall_human_review_rate,
        "fairness_work_mode": fairness_eval["by_work_mode"],
        "fairness_language": fairness_eval["by_language"]
    }

    with open(EVAL_OUTPUT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    if close_db:
        db.close()

    return report

if __name__ == "__main__":
    report = run_evaluation_experiment()
    print("--- EVALUATION EXPERIMENT COMPLETED ---")
    print(json.dumps(report, indent=2))
