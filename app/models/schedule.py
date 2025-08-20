from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class CourseSchedule(BaseModel):
    __tablename__ = "course_schedules"
    
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    schedule_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    registration_start = Column(DateTime(timezone=True), nullable=True)
    registration_end = Column(DateTime(timezone=True), nullable=True)
    
    is_mandatory = Column(Boolean, default=False)
    is_self_paced = Column(Boolean, default=False)
    max_enrollments = Column(Integer, nullable=True)
    current_enrollments = Column(Integer, default=0)
    
    schedule_type = Column(String(50), nullable=False)  # fixed, flexible, self_paced
    delivery_mode = Column(String(50), nullable=False)  # online, blended, in_person
    
    # Time slots for scheduled sessions
    time_slots = Column(JSON, default=list)  # List of session times
    timezone = Column(String(50), default="UTC")
    
    # Prerequisites and requirements
    prerequisites = Column(JSON, default=list)
    enrollment_requirements = Column(JSON, default=dict)
    
    instructor_ids = Column(JSON, default=list)  # List of instructor IDs
    
    status = Column(String(20), default="draft")  # draft, published, active, completed, cancelled
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    enrollments = relationship("UserCourseEnrollment", back_populates="schedule")


class UserCourseEnrollment(BaseModel):
    __tablename__ = "user_course_enrollments"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("course_schedules.id"), nullable=False)
    
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    enrollment_type = Column(String(20), default="voluntary")  # voluntary, mandatory, assigned
    
    status = Column(String(20), default="enrolled")  # enrolled, active, completed, dropped, suspended
    
    start_date = Column(DateTime(timezone=True), nullable=True)
    expected_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    progress_percentage = Column(Float, default=0.0)
    grade = Column(String(5), nullable=True)  # A, B, C, D, F or Pass/Fail
    score = Column(Float, nullable=True)
    
    # Enrollment preferences
    preferred_language = Column(String(10), nullable=True)
    accessibility_needs = Column(JSON, default=dict)
    learning_preferences = Column(JSON, default=dict)
    
    # Tracking
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    total_time_spent_hours = Column(Float, default=0.0)
    
    enrolled_by = Column(UUID(as_uuid=True), nullable=True)  # Who enrolled the user
    
    # Relationships
    schedule = relationship("CourseSchedule", back_populates="enrollments")