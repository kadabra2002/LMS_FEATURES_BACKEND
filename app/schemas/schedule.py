from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class CourseScheduleBase(BaseModel):
    course_id: UUID
    schedule_name: str = Field(max_length=255)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    is_mandatory: bool = False
    is_self_paced: bool = False
    max_enrollments: Optional[int] = Field(None, gt=0)
    schedule_type: str = Field(pattern="^(fixed|flexible|self_paced)$")
    delivery_mode: str = Field(pattern="^(online|blended|in_person)$")
    time_slots: List[Dict[str, Any]] = Field(default_factory=list)
    timezone: str = Field(default="UTC")
    prerequisites: List[str] = Field(default_factory=list)
    enrollment_requirements: Dict[str, Any] = Field(default_factory=dict)
    instructor_ids: List[UUID] = Field(default_factory=list)


class CourseScheduleCreate(CourseScheduleBase):
    created_by: UUID


class CourseScheduleUpdate(BaseModel):
    schedule_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    is_mandatory: Optional[bool] = None
    is_self_paced: Optional[bool] = None
    max_enrollments: Optional[int] = Field(None, gt=0)
    schedule_type: Optional[str] = Field(None, pattern="^(fixed|flexible|self_paced)$")
    delivery_mode: Optional[str] = Field(None, pattern="^(online|blended|in_person)$")
    time_slots: Optional[List[Dict[str, Any]]] = None
    timezone: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    enrollment_requirements: Optional[Dict[str, Any]] = None
    instructor_ids: Optional[List[UUID]] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|active|completed|cancelled)$")


class CourseScheduleResponse(CourseScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    current_enrollments: int
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# User Course Enrollment Schemas
class UserCourseEnrollmentBase(BaseModel):
    user_id: UUID
    course_id: UUID
    schedule_id: UUID
    enrollment_type: str = Field(default="voluntary", pattern="^(voluntary|mandatory|assigned)$")
    expected_completion_date: Optional[datetime] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    accessibility_needs: Dict[str, Any] = Field(default_factory=dict)
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)


class UserCourseEnrollmentCreate(UserCourseEnrollmentBase):
    enrolled_by: Optional[UUID] = None


class UserCourseEnrollmentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(enrolled|active|completed|dropped|suspended)$")
    start_date: Optional[datetime] = None
    expected_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    grade: Optional[str] = Field(None, max_length=5)
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    preferred_language: Optional[str] = Field(None, max_length=10)
    accessibility_needs: Optional[Dict[str, Any]] = None
    learning_preferences: Optional[Dict[str, Any]] = None
    last_activity_date: Optional[datetime] = None
    total_time_spent_hours: Optional[float] = Field(None, ge=0)


class UserCourseEnrollmentResponse(UserCourseEnrollmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    enrollment_date: datetime
    status: str
    start_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    progress_percentage: float
    grade: Optional[str] = None
    score: Optional[float] = None
    last_activity_date: Optional[datetime] = None
    total_time_spent_hours: float
    enrolled_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None