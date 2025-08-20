from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class Assessment(BaseModel):
    __tablename__ = "assessments"
    
    course_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    module_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    assessment_type = Column(String(50), nullable=False)  # quiz, assignment, project, exam
    question_types = Column(JSON, default=list)  # Supported question types
    
    max_score = Column(Float, nullable=False, default=100.0)
    passing_score = Column(Float, nullable=False, default=70.0)
    time_limit_minutes = Column(Integer, nullable=True)
    max_attempts = Column(Integer, default=1)
    
    is_proctored = Column(Boolean, default=False)
    is_randomized = Column(Boolean, default=False)
    show_results_immediately = Column(Boolean, default=True)
    allow_review = Column(Boolean, default=True)
    
    availability_start = Column(DateTime(timezone=True), nullable=True)
    availability_end = Column(DateTime(timezone=True), nullable=True)
    
    weight_in_course = Column(Float, default=1.0)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    questions = relationship("Question", back_populates="assessment")
    user_assessments = relationship("UserAssessment", back_populates="assessment")
    feedback_entries = relationship("Feedback", back_populates="assessment")


class Question(BaseModel):
    __tablename__ = "questions"
    
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # mcq, true_false, matching, essay, etc.
    
    options = Column(JSON, nullable=True)  # For MCQ, matching, etc.
    correct_answer = Column(JSON, nullable=True)  # Correct answer(s)
    explanation = Column(Text, nullable=True)
    
    points = Column(Float, nullable=False, default=1.0)
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    
    order_sequence = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    
    media_url = Column(String(500), nullable=True)  # Image/video URL
    media_type = Column(String(20), nullable=True)  # image, video, audio
    
    tags = Column(JSON, default=list)
    learning_objectives = Column(JSON, default=list)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    user_answers = relationship("UserAnswer", back_populates="question")


class UserAnswer(BaseModel):
    __tablename__ = "user_answers"
    
    user_assessment_id = Column(UUID(as_uuid=True), ForeignKey("user_assessments.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    
    answer = Column(JSON, nullable=True)  # User's answer
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(Float, default=0.0)
    
    time_spent_seconds = Column(Integer, default=0)
    attempt_count = Column(Integer, default=1)
    
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    graded_at = Column(DateTime(timezone=True), nullable=True)
    
    feedback = Column(Text, nullable=True)
    
    # Relationships
    user_assessment = relationship("UserAssessment", back_populates="user_answers")
    question = relationship("Question", back_populates="user_answers")


class Feedback(BaseModel):
    __tablename__ = "feedback"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    
    feedback_type = Column(String(50), nullable=False)  # automated, manual, peer
    feedback_text = Column(Text, nullable=False)
    
    score_given = Column(Float, nullable=True)
    improvement_suggestions = Column(JSON, default=list)
    
    given_by = Column(UUID(as_uuid=True), nullable=True)  # Instructor ID
    given_at = Column(DateTime(timezone=True), server_default=func.now())
    
    is_visible_to_student = Column(Boolean, default=True)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="feedback_entries")