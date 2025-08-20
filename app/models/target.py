from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class Target(BaseModel):
    __tablename__ = "targets"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    module_id = Column(UUID(as_uuid=True), nullable=True)
    
    target_type = Column(String(50), nullable=False)  # course_completion, thesis_submission, exam, certification
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=False)
    estimated_hours = Column(Float, nullable=True)
    
    priority = Column(String(10), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="active")  # active, completed, overdue, cancelled
    
    progress_percentage = Column(Float, default=0.0)
    completion_criteria = Column(JSON, default=dict)  # Specific criteria to meet
    
    is_mandatory = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, nullable=True)  # For recurring targets
    
    assigned_by = Column(UUID(as_uuid=True), nullable=True)  # Who assigned this target
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    meta_data = Column(JSON, default=dict)  # Additional target-specific data
    
    # Relationships
    reminders = relationship("Reminder", back_populates="target")


class Reminder(BaseModel):
    __tablename__ = "reminders"
    
    target_id = Column(UUID(as_uuid=True), ForeignKey("targets.id"), nullable=False)
    
    reminder_type = Column(String(50), nullable=False)  # email, push, sms, in_app
    reminder_time = Column(DateTime(timezone=True), nullable=False)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    is_recurring = Column(Boolean, default=False)
    recurrence_interval_days = Column(Integer, nullable=True)
    
    status = Column(String(20), default="scheduled")  # scheduled, sent, failed, cancelled
    
    # Delivery details
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    
    # Relationships
    target = relationship("Target", back_populates="reminders")