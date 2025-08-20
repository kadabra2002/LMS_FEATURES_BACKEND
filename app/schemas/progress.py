from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ProgressTrackingBase(BaseModel):
    user_id: UUID
    course_id: UUID
    module_id: Optional[UUID] = None
    lesson_id: Optional[UUID] = None
    completion_status: str = Field(default="not_started", pattern="^(not_started|in_progress|completed|failed)$")
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    time_spent_minutes: int = Field(default=0, ge=0)
    quiz_scores: List[float] = Field(default_factory=list)
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    attempts_count: int = Field(default=0, ge=0)


class ProgressTrackingCreate(ProgressTrackingBase):
    pass


class ProgressTrackingUpdate(BaseModel):
    completion_status: Optional[str] = Field(None, pattern="^(not_started|in_progress|completed|failed)$")
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    quiz_scores: Optional[List[float]] = None
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    attempts_count: Optional[int] = Field(None, ge=0)
    last_accessed_at: Optional[datetime] = None


class ProgressTrackingResponse(ProgressTrackingBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# User Assessment Schemas
class UserAssessmentBase(BaseModel):
    user_id: UUID
    assessment_id: UUID
    progress_id: Optional[UUID] = None
    max_score: float = Field(gt=0)
    attempt_number: int = Field(default=1, ge=1)


class UserAssessmentCreate(UserAssessmentBase):
    pass


class UserAssessmentUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0)
    percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    status: Optional[str] = Field(None, pattern="^(not_started|in_progress|completed|graded)$")
    completed_at: Optional[datetime] = None
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    answers: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None


class UserAssessmentResponse(UserAssessmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    score: Optional[float] = None
    percentage: Optional[float] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None
    time_spent_minutes: int
    answers: Dict[str, Any]
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Attendance Schemas
class AttendanceBase(BaseModel):
    user_id: UUID
    session_id: UUID
    course_id: UUID
    module_id: Optional[UUID] = None
    session_type: str = Field(pattern="^(live|recorded|interactive)$")
    attended_at: datetime
    duration_minutes: int = Field(default=0, ge=0)
    status: str = Field(default="present", pattern="^(present|absent|late|partial)$")


class AttendanceCreate(AttendanceBase):
    device_type: Optional[str] = None
    platform: Optional[str] = None


class AttendanceUpdate(BaseModel):
    duration_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(present|absent|late|partial)$")
    interaction_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    leave_time: Optional[datetime] = None


class AttendanceResponse(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    progress_id: Optional[UUID] = None
    interaction_score: Optional[float] = None
    join_time: Optional[datetime] = None
    leave_time: Optional[datetime] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None