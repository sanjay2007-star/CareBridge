from sqlalchemy.orm import Session
from backend.models import StaffUser, StaffCapacity

def check_and_allocate_staff_capacity(db: Session, staff_id: str) -> tuple[bool, str, int]:
    """
    Checks staff capacity before assignment.
    Returns: (is_available, status_message, available_slots)
    """
    staff = db.query(StaffUser).filter(StaffUser.staff_id == staff_id).first()
    if not staff:
        return False, "Staff member not found", 0

    available_slots = staff.maximum_active_cases - staff.current_active_cases
    staff.available_slots = max(0, available_slots)
    db.commit()

    if staff.current_active_cases >= staff.maximum_active_cases:
        return False, f"Staff member {staff.name} is at maximum capacity ({staff.current_active_cases}/{staff.maximum_active_cases}). Case placed on WAITLIST / MANUAL SCHEDULING REQUIRED.", 0

    return True, f"Capacity available ({available_slots} slots remaining).", available_slots

def recommend_available_staff(db: Session, role: str) -> list[dict]:
    """
    Ranks available staff members by workload and available slots.
    """
    staff_list = db.query(StaffUser).filter(StaffUser.role == role.lower()).all()
    available = []
    for s in staff_list:
        slots = s.maximum_active_cases - s.current_active_cases
        if slots > 0:
            available.append({
                "staff_id": s.staff_id,
                "name": s.name,
                "role": s.role,
                "maximum_active_cases": s.maximum_active_cases,
                "current_active_cases": s.current_active_cases,
                "available_slots": slots
            })
    # Sort by available slots descending (workload optimization)
    available.sort(key=lambda x: x["available_slots"], reverse=True)
    return available
