import re
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from backend.models import ConsentRecord

CATEGORY_KEYWORDS = {
    "workplace": ["workplace", "workload", "burnout", "job", "career", "manager", "team", "overtime", "deadline", "project lead", "performance metrics", "role ambiguity"],
    "financial": ["financial", "debt", "budget", "loan", "expenses", "cost of living", "salary", "monetary", "money", "affordability", "medical expenses"],
    "family": ["family", "marital", "spouse", "marriage", "childcare", "parents", "child", "bereavement", "domestic", "divorce", "adolescent", "caregiving"],
    "wellbeing": ["anxiety", "sleep", "stress", "mindfulness", "panic", "self-care", "wellbeing", "mental health", "burnout symptoms"],
    "housing": ["housing", "lease", "landlord", "relocation", "tenancy", "tenant", "rent escalation", "rent affordability"],
    "legal_support": ["legal", "contract", "estate", "court", "attorney", "lawyer", "divorce proceedings"],
    "general_progress": ["progress", "goals", "session", "check-in", "satisfaction", "boundary setting", "improvement"]
}

def classify_text_segments(text: str) -> List[Dict[str, any]]:
    """
    Splits session summary into sentences and assigns matching information categories.
    """
    # Split text into sentences
    sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', text) if s.strip()]
    classified_segments = []

    for sentence in sentences:
        sentence_lower = sentence.lower()
        matched_categories = set()
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in sentence_lower:
                    matched_categories.add(cat)

        if not matched_categories:
            matched_categories.add("general_progress")

        classified_segments.append({
            "sentence": sentence,
            "categories": list(matched_categories)
        })

    return classified_segments

def is_category_consented(db: Session, client_id: str, category: str, recipient_role: str) -> bool:
    """
    DETERMINISTIC CONSENT ENGINE:
    Checks if explicit active consent exists for category and recipient role.
    Privacy-by-default: If record missing, expired, or revoked -> False.
    """
    records = db.query(ConsentRecord).filter(
        ConsentRecord.client_id == client_id,
        ConsentRecord.information_category == category
    ).all()

    if not records:
        return False

    for rec in records:
        if rec.consent_status == "granted" and rec.revoked_at is None:
            # Role check
            allowed = rec.allowed_recipient_role.lower()
            target_role = recipient_role.lower()
            if allowed == "all" or allowed == target_role:
                return True

    return False

def filter_session_data(db: Session, client_id: str, session_summary: str, recipient_role: str) -> Tuple[str, List[str], List[str]]:
    """
    Filters session summary so ONLY consent-approved information is retained.
    Returns: (filtered_text, approved_categories, restricted_categories)
    """
    segments = classify_text_segments(session_summary)
    approved_sentences = []
    approved_cats = set()
    restricted_cats = set()

    for seg in segments:
        sentence = seg["sentence"]
        categories = seg["categories"]

        # All categories in this sentence must be consented for it to pass
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
