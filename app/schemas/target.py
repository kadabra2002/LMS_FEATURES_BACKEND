from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class TargetBase(BaseModel):
    user_id: UUID
    course_id: Optional[UUID] = None
    module_id: Optional[UUID] = None
    target_type: str = Field(pattern="^(course_completion|thesis_submission|exam|certification|project_deadline|skill_assessment)$")
    title: str = Field(max_length=255)
    description: Optional[str] = None
    deadline: datetime
    estimated_hours: Optional[float] = Field(None, gt=0)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    completion_criteria: Dict[str, Any] = Field(default_factory=dict)
    is_mandatory: bool = False
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TargetCreate(TargetBase):
    start_date: Optional[datetime] = None
    assigned_by: Optional[UUID] = None


class TargetUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, gt=0)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(active|completed|overdue|cancelled)$")
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    completion_criteria: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class TargetResponse(TargetBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    start_date: Optional[datetime] = None
    status: str
    progress_percentage: float
    assigned_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Reminder Schemas
class ReminderBase(BaseModel):
    target_id: UUID
    reminder_type: str = Field(pattern="^(email|push|sms|in_app)$")
    reminder_time: datetime
    title: str = Field(max_length=255)
    message: str
    is_recurring: bool = False
    recurrence_interval_days: Optional[int] = Field(None, gt=0)


class ReminderCreate(ReminderBase):
    recipient_email: Optional[str] = Field(None, max_length=255)
    recipient_phone: Optional[str] = Field(None, max_length=20)


class ReminderUpdate(BaseModel):
    reminder_time: Optional[datetime] = None
    title: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|sent|failed|cancelled)$")
    is_recurring: Optional[bool] = None
    recurrence_interval_days: Optional[int] = Field(None, gt=0)
    recipient_email: Optional[str] = Field(None, max_length=255)
    recipient_phone: Optional[str] = Field(None, max_length=20)


class ReminderResponse(ReminderBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_sent: bool
    sent_at: Optional[datetime] = None
    status: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None