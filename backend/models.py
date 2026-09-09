from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from datetime import datetime
from backend.database import Base

class Client(Base):
    __tablename__ = "clients"

    client_id = Column(String, primary_key=True, index=True)
    age_group = Column(String, nullable=False)
    work_mode = Column(String, nullable=False) # Remote, Hybrid, On-site
    preferred_language = Column(String, nullable=False) # English-primary, Multilingual/non-English-primary
    region = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StaffUser(Base):
    __tablename__ = "staff_users"

    staff_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False) # counsellor, social_worker, admin
    specialisation = Column(String, nullable=True)
    maximum_active_cases = Column(Integer, default=20)
    current_active_cases = Column(Integer, default=0)
    available_slots = Column(Integer, default=20)

class SessionRecord(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False, index=True)
    counsellor_id = Column(String, ForeignKey("staff_users.staff_id"), nullable=False)
    session_date = Column(String, nullable=False)
    session_summary = Column(Text, nullable=False)
    sensitivity_level = Column(String, default="Medium") # Low, Medium, High
    created_at = Column(DateTime, default=datetime.utcnow)

class ClientGoal(Base):
    __tablename__ = "client_goals"

    goal_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False, index=True)
    goal_category = Column(String, nullable=False)
    goal_description = Column(Text, nullable=False)
    goal_status = Column(String, default="Active") # Active, Achieved, Paused
    created_at = Column(DateTime, default=datetime.utcnow)

class ConsentRecord(Base):
    __tablename__ = "consents"

    consent_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False, index=True)
    information_category = Column(String, nullable=False) # workplace, financial, family, wellbeing, housing, legal_support, general_progress
    allowed_recipient_role = Column(String, nullable=False) # counsellor, social_worker, all
    consent_status = Column(String, nullable=False) # granted, revoked
    granted_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

class PendingAction(Base):
    __tablename__ = "pending_actions"

    action_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False, index=True)
    assigned_role = Column(String, nullable=False) # counsellor, social_worker
    action_description = Column(Text, nullable=False)
    priority = Column(String, default="Medium") # High, Medium, Low
    due_date = Column(String, nullable=False)
    status = Column(String, default="Pending") # Pending, In Progress, Completed

class HandoverRecord(Base):
    __tablename__ = "handovers"

    handover_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"), nullable=False, index=True)
    from_staff_id = Column(String, ForeignKey("staff_users.staff_id"), nullable=False)
    to_staff_id = Column(String, ForeignKey("staff_users.staff_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    handover_status = Column(String, default="Pending Review") # Pending Review, Approved, Human Review Required, Waitlisted
    confidence_score = Column(Float, default=1.0)
    requires_human_review = Column(Boolean, default=False)
    baseline_summary = Column(Text, nullable=True)
    prototype_summary = Column(Text, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    client_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    result = Column(String, nullable=False) # SUCCESS, FORBIDDEN, ERROR

class StaffCapacity(Base):
    __tablename__ = "staff_capacities"

    staff_id = Column(String, ForeignKey("staff_users.staff_id"), primary_key=True, index=True)
    role = Column(String, nullable=False)
    maximum_active_cases = Column(Integer, default=20)
    current_active_cases = Column(Integer, default=0)
    available_slots = Column(Integer, default=20)
