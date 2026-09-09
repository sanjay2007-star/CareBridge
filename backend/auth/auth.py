from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from backend.database import get_db
from backend.models import AuditLog

def log_audit(db: Session, user_id: str, client_id: str, action: str, resource_type: str, result: str):
    audit_entry = AuditLog(
        audit_id=f"AUD_{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        client_id=client_id,
        action=action,
        resource_type=resource_type,
        timestamp=datetime.utcnow(),
        result=result
    )
    db.add(audit_entry)
    db.commit()

class CurrentUser:
    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role.lower()

def get_current_user(
    x_user_id: str = Header(default="COUNS_001"),
    x_user_role: str = Header(default="counsellor")
) -> CurrentUser:
    return CurrentUser(user_id=x_user_id, role=x_user_role)

def require_role(allowed_roles: list):
    def role_checker(current_user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
        if current_user.role not in allowed_roles:
            log_audit(
                db=db,
                user_id=current_user.user_id,
                client_id="N/A",
                action=f"ACCESS_DENIED_ROLE_{current_user.role.upper()}",
                resource_type="PROTECTED_ENDPOINT",
                result="FORBIDDEN"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not authorized to access this resource."
            )
        return current_user
    return role_checker
