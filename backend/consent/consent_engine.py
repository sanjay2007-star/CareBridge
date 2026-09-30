"""
Consent Engine Module
=====================
Provides deterministic privacy filtering and classification rules for EAP session notes.

Key Architecture Principles:
1. Privacy-by-Default: Information categories missing an explicit granted consent record evaluate to False.
2. Recipient Role Scoping: Consent verification evaluates both category consent status and target staff role.
3. Sentence-Level Granular Filtering: Session summaries are segmented into sentences; any sentence containing unapproved categories is stripped prior to handover text generation.
"""

import re
from typing import List, Dict, Tuple, Any
from sqlalchemy.orm import Session
from backend.models import ConsentRecord

# Taxonomic Keyword Registry for Rule-Based Information Classification
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "workplace": [
        "workplace", "workload", "burnout", "job", "career", "manager", "team",
        "overtime", "deadline", "project lead", "performance metrics", "role ambiguity"
    ],
    "financial": [
        "financial", "debt", "budget", "loan", "expenses", "cost of living",
        "salary", "monetary", "money", "affordability", "medical expenses"
    ],
    "family": [
        "family", "marital", "spouse", "marriage", "childcare", "parents",
        "child", "bereavement", "domestic", "divorce", "adolescent", "caregiving"
    ],
    "wellbeing": [
        "anxiety", "sleep", "stress", "mindfulness", "panic", "self-care",
        "wellbeing", "mental health", "burnout symptoms"
    ],
    "housing": [
        "housing", "lease", "landlord", "relocation", "tenancy", "tenant",
        "rent escalation", "rent affordability"
    ],
    "legal_support": [
        "legal", "contract", "estate", "court", "attorney", "lawyer", "divorce proceedings"
    ],
    "general_progress": [
        "progress", "goals", "session", "check-in", "satisfaction", "boundary setting", "improvement"
    ]
}

def classify_text_segments(text: str) -> List[Dict[str, Any]]:
    """
    Classifies raw session notes into sentence-level segments mapped to information categories.

    Args:
        text (str): Raw confidential counselling session text.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing individual sentences and matched categories.
    """
    if not text:
        return []

    # Tokenize text into discrete sentences using punctuation boundaries
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if s.strip()]
    classified_segments = []

    for sentence in sentences:
        sentence_lower = sentence.lower()
        matched_categories = set()

        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in sentence_lower:
                    matched_categories.add(cat)

        # Fallback category for general non-sensitive progress notes
        if not matched_categories:
            matched_categories.add("general_progress")

        classified_segments.append({
            "sentence": sentence,
            "categories": list(matched_categories)
        })

    return classified_segments

def is_category_consented(db: Session, client_id: str, category: str, recipient_role: str) -> bool:
    """
    DETERMINISTIC CONSENT ENGINE VERIFICATION:
    Evaluates whether explicit, active client consent exists for a specific information category
    and recipient role.

    Rules:
    - Missing record -> False (Privacy-by-default)
    - Revoked status (`consent_status == "revoked"` or `revoked_at` is set) -> False
    - Recipient role mismatch (e.g. granted for 'counsellor' when recipient is 'social_worker') -> False
    - Active granted status (`consent_status == "granted"` AND `allowed_recipient_role` match) -> True

    Args:
        db (Session): SQLAlchemy database session.
        client_id (str): Target client identifier.
        category (str): Information category key (e.g., 'financial', 'family').
        recipient_role (str): Role of recipient staff ('counsellor', 'social_worker', 'admin').

    Returns:
        bool: True if consent is explicitly granted and valid for recipient role; False otherwise.
    """
    records = db.query(ConsentRecord).filter(
        ConsentRecord.client_id == client_id,
        ConsentRecord.information_category == category
    ).all()

    if not records:
        return False

    for rec in records:
        if rec.consent_status == "granted" and rec.revoked_at is None:
            allowed = rec.allowed_recipient_role.lower()
            target_role = recipient_role.lower()
            if allowed == "all" or allowed == target_role:
                return True

    return False

def filter_session_data(db: Session, client_id: str, session_summary: str, recipient_role: str) -> Tuple[str, List[str], List[str]]:
    """
    Filters raw session summary text so ONLY consent-approved sentences are retained for handover.

    Args:
        db (Session): Database session context.
        client_id (str): Client ID whose consent rules are checked.
        session_summary (str): Raw text of the counselling session note.
        recipient_role (str): Recipient staff member role.

    Returns:
        Tuple[str, List[str], List[str]]:
            - filtered_text (str): Safe text containing only consented sentences.
            - approved_categories (List[str]): List of approved categories included.
            - restricted_categories (List[str]): List of restricted categories stripped out.
    """
    segments = classify_text_segments(session_summary)
    approved_sentences = []
    approved_cats = set()
    restricted_cats = set()

    for seg in segments:
        sentence = seg["sentence"]
        categories = seg["categories"]

        # Sentence passes ONLY if all identified categories pass consent verification
        sentence_consented = True
        for cat in categories:
            if is_category_consented(db, client_id, cat, recipient_role):
                approved_cats.add(cat)
            else:
                restricted_cats.add(cat)
                sentence_consented = False

        if sentence_consented:
            approved_sentences.append(sentence)

    filtered_text = " ".join(approved_sentences)
    return filtered_text, list(approved_cats), list(restricted_cats)
