from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class LearningPathBase(BaseModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    skill_level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    estimated_duration_hours: Optional[float] = Field(None, gt=0)
    difficulty_level: int = Field(default=1, ge=1, le=10)
    is_adaptive: bool = True
    is_mandatory: bool = False
    is_active: bool = True
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class LearningPathCreate(LearningPathBase):
    created_by: UUID


class LearningPathUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    skill_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    estimated_duration_hours: Optional[float] = Field(None, gt=0)
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    is_adaptive: Optional[bool] = None
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class LearningPathResponse(LearningPathBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# Learning Path Course Schemas
class LearningPathCourseBase(BaseModel):
    path_id: UUID
    course_id: UUID
    order_sequence: int = Field(ge=1)
    is_mandatory: bool = True
    weight: float = Field(default=1.0, gt=0)
    prerequisites: List[str] = Field(default_factory=list)
    unlock_criteria: Dict[str, Any] = Field(default_factory=dict)
    estimated_duration_hours: Optional[float] = Field(None, gt=0)
    points_awarded: int = Field(default=0, ge=0)


class LearningPathCourseCreate(LearningPathCourseBase):
    pass


class LearningPathCourseResponse(LearningPathCourseBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# User Learning Path Schemas
class UserLearningPathBase(BaseModel):
    user_id: UUID
    path_id: UUID
    target_completion_date: Optional[datetime] = None
    current_course_id: Optional[UUID] = None
    current_step: int = Field(default=1, ge=1)
    personalization_data: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserLearningPathCreate(UserLearningPathBase):
    pass


class UserLearningPathUpdate(BaseModel):
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    current_course_id: Optional[UUID] = None
    current_step: Optional[int] = Field(None, ge=1)
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    status: Optional[str] = Field(None, pattern="^(enrolled|active|completed|dropped|suspended)$")
    personalization_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    points_earned: Optional[int] = Field(None, ge=0)


class UserLearningPathResponse(UserLearningPathBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    enrollment_date: datetime
    start_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    total_steps: Optional[int] = None
    progress_percentage: float
    status: str
    points_earned: int
    certificates_earned: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None