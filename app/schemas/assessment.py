from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AssessmentBase(BaseModel):
    course_id: UUID
    module_id: Optional[UUID] = None
    title: str = Field(max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    assessment_type: str = Field(pattern="^(quiz|assignment|project|exam)$")
    question_types: List[str] = Field(default_factory=list)
    max_score: float = Field(default=100.0, gt=0)
    passing_score: float = Field(default=70.0, gt=0)
    time_limit_minutes: Optional[int] = Field(None, gt=0)
    max_attempts: int = Field(default=1, ge=1)
    is_proctored: bool = False
    is_randomized: bool = False
    show_results_immediately: bool = True
    allow_review: bool = True
    weight_in_course: float = Field(default=1.0, gt=0)


class AssessmentCreate(AssessmentBase):
    created_by: UUID
    availability_start: Optional[datetime] = None
    availability_end: Optional[datetime] = None


class AssessmentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    max_score: Optional[float] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, gt=0)
    time_limit_minutes: Optional[int] = Field(None, gt=0)
    max_attempts: Optional[int] = Field(None, ge=1)
    is_proctored: Optional[bool] = None
    is_randomized: Optional[bool] = None
    show_results_immediately: Optional[bool] = None
    allow_review: Optional[bool] = None
    availability_start: Optional[datetime] = None
    availability_end: Optional[datetime] = None
    weight_in_course: Optional[float] = Field(None, gt=0)


class AssessmentResponse(AssessmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    availability_start: Optional[datetime] = None
    availability_end: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# Question Schemas
class QuestionBase(BaseModel):
    assessment_id: UUID
    question_text: str
    question_type: str = Field(pattern="^(mcq|true_false|matching|essay|fill_blank|multiple_response)$")
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    points: float = Field(default=1.0, gt=0)
    difficulty_level: int = Field(default=1, ge=1, le=5)
    order_sequence: int = Field(ge=1)
    is_required: bool = True
    media_url: Optional[str] = Field(None, max_length=500)
    media_type: Optional[str] = Field(None, pattern="^(image|video|audio)$")
    tags: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = Field(None, pattern="^(mcq|true_false|matching|essay|fill_blank|multiple_response)$")
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    points: Optional[float] = Field(None, gt=0)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    order_sequence: Optional[int] = Field(None, ge=1)
    is_required: Optional[bool] = None
    media_url: Optional[str] = Field(None, max_length=500)
    media_type: Optional[str] = Field(None, pattern="^(image|video|audio)$")
    tags: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None


class QuestionResponse(QuestionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# User Answer Schemas
class UserAnswerBase(BaseModel):
    user_assessment_id: UUID
    question_id: UUID
    answer: Optional[Dict[str, Any]] = None
    time_spent_seconds: int = Field(default=0, ge=0)
    attempt_count: int = Field(default=1, ge=1)


class UserAnswerCreate(UserAnswerBase):
    pass


class UserAnswerResponse(UserAnswerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_correct: Optional[bool] = None
    points_earned: float
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    feedback: Optional[str] = None


# Feedback Schemas
class FeedbackBase(BaseModel):
    user_id: UUID
    assessment_id: UUID
    feedback_type: str = Field(pattern="^(automated|manual|peer)$")
    feedback_text: str
    score_given: Optional[float] = Field(None, ge=0)
    improvement_suggestions: List[str] = Field(default_factory=list)
    is_visible_to_student: bool = True


class FeedbackCreate(FeedbackBase):
    given_by: Optional[UUID] = None


class FeedbackResponse(FeedbackBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    given_by: Optional[UUID] = None
    given_at: datetime