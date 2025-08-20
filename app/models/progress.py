from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class ProgressTracking(BaseModel):
    __tablename__ = "progress_tracking"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    module_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    lesson_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    completion_status = Column(String(20), default="not_started")  # not_started, in_progress, completed, failed
    completion_percentage = Column(Float, default=0.0)
    time_spent_minutes = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    quiz_scores = Column(JSON, default=list)  # List of quiz scores
    overall_score = Column(Float, nullable=True)
    attempts_count = Column(Integer, default=0)
    
    # Relationships
    assessments = relationship("UserAssessment", back_populates="progress")
    attendance_records = relationship("Attendance", back_populates="progress")


class UserAssessment(BaseModel):
    __tablename__ = "user_assessments"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    progress_id = Column(UUID(as_uuid=True), ForeignKey("progress_tracking.id"), nullable=True)
    
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=True)
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed, graded
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    graded_at = Column(DateTime(timezone=True), nullable=True)
    
    time_spent_minutes = Column(Integer, default=0)
    attempt_number = Column(Integer, default=1)
    
    answers = Column(JSON, default=dict)  # Store user answers
    feedback = Column(Text, nullable=True)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="user_assessments")
    progress = relationship("ProgressTracking", back_populates="assessments")
    user_answers = relationship("UserAnswer", back_populates="user_assessment")


class Attendance(BaseModel):
    __tablename__ = "attendance"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    module_id = Column(UUID(as_uuid=True), nullable=True)
    progress_id = Column(UUID(as_uuid=True), ForeignKey("progress_tracking.id"), nullable=True)
    
    session_type = Column(String(20), nullable=False)  # live, recorded, interactive
    attended_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=0)
    
    status = Column(String(20), default="present")  # present, absent, late, partial
    interaction_score = Column(Float, nullable=True)  # Engagement score
    
    join_time = Column(DateTime(timezone=True), nullable=True)
    leave_time = Column(DateTime(timezone=True), nullable=True)
    
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    platform = Column(String(50), nullable=True)  # web, app
    
    # Relationships
    progress = relationship("ProgressTracking", back_populates="attendance_records")