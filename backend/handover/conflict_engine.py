"""
Section 10 Conflict Detection Engine Module
==========================================
Scans historical session summaries and clinical records to identify contradictory statements,
clinical trajectory divergence, or operational incompatibilities across inter-professional handovers.

Core Mechanics:
1. Temporal Pair-wise Scanning: Sorts session notes chronologically and evaluates all session pairs (S_i, S_j).
2. Opposing Keyword Taxonomy: Scans for mutually exclusive statement pairings across employment status, relocation, substance safety, and clinical stress trajectories.
3. Severity Rating & Confidence Penalty: Assigns confidence penalties (0.40 CRITICAL, 0.30 HIGH, 0.15 MEDIUM) and flags mandatory Human Review guardrails.
"""

import re
from typing import List, Dict, Tuple, Any

# Section 10 Opposing Keyword Pair Taxonomy & Severity Weight Matrix
OPPOSING_KEYWORD_PAIRS = [
    {
        "category": "Employment Status",
        "pair": (
            ["relocate", "relocating", "move overseas", "transfer branch"],
            ["remain on-site", "stay local", "cancel transfer", "local branch"]
        ),
        "severity": "CRITICAL",
        "description": "Contradictory relocation vs local retention plans across sessions."
    },
    {
        "category": "Employment Status",
        "pair": (
            ["full time", "full-time", "continuing employment"],
            ["resigned", "resignation", "terminated", "leave company"]
        ),
        "severity": "CRITICAL",
        "description": "Contradictory employment retention vs resignation statements."
    },
    {
        "category": "Clinical Stress Trajectory",
        "pair": (
            ["high workload", "severe burnout", "extreme pressure", "overwhelmed"],
            ["minimal stress", "manageable workload", "no burnout", "well-adjusted"]
        ),
        "severity": "HIGH",
        "description": "Unexplained rapid contradiction between severe burnout and zero stress."
    },
    {
        "category": "Substance & Safety",
        "pair": (
            ["no substance use", "denies alcohol use", "sober"],
            ["active alcohol misuse", "substance relapse", "heavy drinking"]
        ),
        "severity": "CRITICAL",
        "description": "Contradictory clinical statements regarding substance use and safety."
    },
    {
        "category": "Housing & Residence",
        "pair": (
            ["stable housing", "lease signed", "secure home"],
            ["eviction notice", "housing instability", "homelessness risk"]
        ),
        "severity": "HIGH",
        "description": "Contradictory statements regarding housing security."
    },
    {
        "category": "Family Support System",
        "pair": (
            ["strong family support", "reconciled with spouse"],
            ["domestic dispute", "family isolation", "divorce final"]
        ),
        "severity": "MEDIUM",
        "description": "Contradictory family support system reporting."
    }
]

def detect_conflicts(session_summaries: List[Dict[str, Any]]) -> Tuple[bool, float, List[Dict[str, Any]]]:
    """
    SECTION 10 CONFLICT DETECTION ALGORITHM:
    Evaluates historical session records for contradictory clinical or operational statements.

    Algorithm Steps:
    1. Verify session count >= 2.
    2. Sort sessions chronologically by `session_date`.
    3. Evaluate pairwise session combinations (S_i, S_j) against OPPOSING_KEYWORD_PAIRS.
    4. Compute maximum confidence penalty:
       - CRITICAL severity -> 0.40 penalty
       - HIGH severity     -> 0.30 penalty
       - MEDIUM severity   -> 0.15 penalty
    5. Return flag list and maximum penalty to trigger Safe Fallback Guardrails.

    Args:
        session_summaries (List[Dict[str, Any]]): Session dicts containing `session_id`, `session_date`, and `session_summary`.

    Returns:
        Tuple[bool, float, List[Dict[str, Any]]]:
            - has_conflict (bool): True if at least one contradiction is detected.
            - max_penalty (float): Maximum confidence score penalty deduction.
            - conflict_flags (List[Dict]): Detailed list of detected conflict flags.
    """
    if len(session_summaries) < 2:
        return False, 0.0, []

    conflict_flags = []
    max_penalty = 0.0

    # Chronological ordering of sessions
    sorted_sessions = sorted(session_summaries, key=lambda s: s.get("session_date", ""))

    # Pairwise historical session comparison
    for i in range(len(sorted_sessions)):
        for j in range(i + 1, len(sorted_sessions)):
            sess_a = sorted_sessions[i]
            sess_b = sorted_sessions[j]
            text_a = sess_a.get("session_summary", "").lower()
            text_b = sess_b.get("session_summary", "").lower()

            for rule in OPPOSING_KEYWORD_PAIRS:
                kw_set_1, kw_set_2 = rule["pair"]
                match_a_1 = any(kw in text_a for kw in kw_set_1)
                match_b_2 = any(kw in text_b for kw in kw_set_2)

                match_a_2 = any(kw in text_a for kw in kw_set_2)
                match_b_1 = any(kw in text_b for kw in kw_set_1)

                if (match_a_1 and match_b_2) or (match_a_2 and match_b_1):
                    sev = rule["severity"]
                    penalty = 0.40 if sev == "CRITICAL" else (0.30 if sev == "HIGH" else 0.15)
                    if penalty > max_penalty:
                        max_penalty = penalty

                    conflict_flags.append({
                        "session_id_1": sess_a.get("session_id"),
                        "session_date_1": sess_a.get("session_date"),
                        "session_id_2": sess_b.get("session_id"),
                        "session_date_2": sess_b.get("session_date"),
                        "conflict_category": rule["category"],
                        "severity": sev,
                        "description": rule["description"],
                        "confidence_penalty": penalty
                    })

    has_conflict = len(conflict_flags) > 0
    return has_conflict, max_penalty, conflict_flags
