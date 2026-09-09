from typing import List, Dict
import pandas as pd

def evaluate_subgroup_fairness(results: List[Dict]) -> Dict:
    """
    Evaluates baseline vs prototype performance across Work Mode and Language Group.
    """
    df = pd.DataFrame(results)
    if df.empty:
        return {"by_work_mode": {}, "by_language": {}}

    # Group by Work Mode
    work_mode_group = df.groupby("work_mode").agg(
        total_handovers=("client_id", "count"),
        avg_baseline_repetition=("baseline_repetition", "mean"),
        avg_proto_repetition=("proto_repetition", "mean"),
        repetition_reduction=("repetition_reduction", "mean"),
        consent_violation_rate=("consent_violations", "sum"),
        total_restricted=("total_restricted", "sum"),
        completeness=("completeness", "mean"),
        action_recall=("action_recall", "mean"),
        human_review_rate=("human_review", "mean")
    ).reset_index()

    work_mode_res = {}
    for _, row in work_mode_group.iterrows():
        total_restr = row["total_restricted"]
        viol_rate = (row["consent_violation_rate"] / total_restr * 100.0) if total_restr > 0 else 0.0
        work_mode_res[row["work_mode"]] = {
            "total_handovers": int(row["total_handovers"]),
            "repetition_reduction": round(float(row["repetition_reduction"]), 2),
            "consent_violation_rate": round(float(viol_rate), 2),
            "summary_completeness": round(float(row["completeness"]), 2),
            "pending_action_recall": round(float(row["action_recall"]), 2),
            "human_review_rate": round(float(row["human_review_rate"] * 100.0), 2)
        }

    # Group by Language
    language_group = df.groupby("preferred_language").agg(
        total_handovers=("client_id", "count"),
        avg_baseline_repetition=("baseline_repetition", "mean"),
        avg_proto_repetition=("proto_repetition", "mean"),
        repetition_reduction=("repetition_reduction", "mean"),
        consent_violation_rate=("consent_violations", "sum"),
        total_restricted=("total_restricted", "sum"),
        completeness=("completeness", "mean"),
        action_recall=("action_recall", "mean"),
        human_review_rate=("human_review", "mean")
    ).reset_index()

    lang_res = {}
    for _, row in language_group.iterrows():
        total_restr = row["total_restricted"]
        viol_rate = (row["consent_violation_rate"] / total_restr * 100.0) if total_restr > 0 else 0.0
        lang_res[row["preferred_language"]] = {
            "total_handovers": int(row["total_handovers"]),
            "repetition_reduction": round(float(row["repetition_reduction"]), 2),
            "consent_violation_rate": round(float(viol_rate), 2),
            "summary_completeness": round(float(row["completeness"]), 2),
            "pending_action_recall": round(float(row["action_recall"]), 2),
            "human_review_rate": round(float(row["human_review_rate"] * 100.0), 2)
        }

    return {
        "by_work_mode": work_mode_res,
        "by_language": lang_res
    }
