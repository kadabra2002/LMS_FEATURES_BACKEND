from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class ActivityTemplate(BaseModel):
    __tablename__ = "activity_templates"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    activity_type = Column(String(50), nullable=False)  # video, quiz, assignment, discussion, etc.
    category = Column(String(100), nullable=True)
    
    template_data = Column(JSON, nullable=False)  # Template structure and content
    default_settings = Column(JSON, default=dict)  # Default configuration
    
    estimated_duration_minutes = Column(Integer, nullable=True)
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    
    is_public = Column(Boolean, default=False)  # Can be used by other instructors
    is_reusable = Column(Boolean, default=True)
    
    usage_count = Column(Integer, default=0)  # How many times it's been used
    rating = Column(Float, nullable=True)  # Average rating from users
    
    tags = Column(JSON, default=list)
    learning_objectives = Column(JSON, default=list)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    activities = relationship("Activity", back_populates="template")


class Activity(BaseModel):
    __tablename__ = "activities"
    
    template_id = Column(UUID(as_uuid=True), ForeignKey("activity_templates.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    activity_type = Column(String(50), nullable=False)  # video, quiz, assignment, discussion, etc.
    content = Column(JSON, nullable=False)  # Activity content and configuration
    
    estimated_duration_minutes = Column(Integer, nullable=True)
    max_score = Column(Float, nullable=True)
    passing_score = Column(Float, nullable=True)
    
    is_mandatory = Column(Boolean, default=True)
    is_graded = Column(Boolean, default=False)
    allow_multiple_attempts = Column(Boolean, default=True)
    max_attempts = Column(Integer, nullable=True)
    
    # Availability
    available_from = Column(DateTime(timezone=True), nullable=True)
    available_until = Column(DateTime(timezone=True), nullable=True)
    
    # Settings
    settings = Column(JSON, default=dict)  # Activity-specific settings
    resources = Column(JSON, default=list)  # Associated resources
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    template = relationship("ActivityTemplate", back_populates="activities")
    course_activities = relationship("CourseActivity", back_populates="activity")


class CourseActivity(BaseModel):
    __tablename__ = "course_activities"
    
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    module_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.id"), nullable=False)
    
    order_sequence = Column(Integer, nullable=False)
    
    # Course-specific overrides
    title_override = Column(String(255), nullable=True)
    description_override = Column(Text, nullable=True)
    settings_override = Column(JSON, default=dict)
    
    weight_in_grade = Column(Float, default=1.0)
    is_required = Column(Boolean, default=True)
    
    # Availability overrides
    available_from_override = Column(DateTime(timezone=True), nullable=True)
    available_until_override = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    activity = relationship("Activity", back_populates="course_activities")