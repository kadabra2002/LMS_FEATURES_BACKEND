from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class LearningPath(BaseModel):
    __tablename__ = "learning_paths"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    skill_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    estimated_duration_hours = Column(Float, nullable=True)
    difficulty_level = Column(Integer, default=1)  # 1-10 scale
    
    is_adaptive = Column(Boolean, default=True)
    is_mandatory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    prerequisites = Column(JSON, default=list)  # List of required skills/courses
    learning_objectives = Column(JSON, default=list)  # List of learning goals
    tags = Column(JSON, default=list)  # Tags for filtering
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    path_courses = relationship("LearningPathCourse", back_populates="learning_path")
    user_paths = relationship("UserLearningPath", back_populates="learning_path")


class LearningPathCourse(BaseModel):
    __tablename__ = "learning_path_courses"
    
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    order_sequence = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    weight = Column(Float, default=1.0)  # Importance weight in the path
    
    prerequisites = Column(JSON, default=list)  # Course-specific prerequisites
    unlock_criteria = Column(JSON, default=dict)  # Criteria to unlock this course
    
    estimated_duration_hours = Column(Float, nullable=True)
    points_awarded = Column(Integer, default=0)
    
    # Relationships
    learning_path = relationship("LearningPath", back_populates="path_courses")


class UserLearningPath(BaseModel):
    __tablename__ = "user_learning_paths"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    path_id = Column(UUID(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)
    
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)
    
    current_course_id = Column(UUID(as_uuid=True), nullable=True)
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, nullable=True)
    
    progress_percentage = Column(Float, default=0.0)
    status = Column(String(20), default="enrolled")  # enrolled, active, completed, dropped, suspended
    
    personalization_data = Column(JSON, default=dict)  # Adaptive learning data
    preferences = Column(JSON, default=dict)  # User learning preferences
    
    points_earned = Column(Integer, default=0)
    certificates_earned = Column(JSON, default=list)
    
    # Relationships
    learning_path = relationship("LearningPath", back_populates="user_paths")