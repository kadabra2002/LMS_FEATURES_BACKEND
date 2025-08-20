from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ActivityTemplateBase(BaseModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    activity_type: str = Field(pattern="^(video|quiz|assignment|discussion|simulation|reading|project)$")
    category: Optional[str] = Field(None, max_length=100)
    template_data: Dict[str, Any]
    default_settings: Dict[str, Any] = Field(default_factory=dict)
    estimated_duration_minutes: Optional[int] = Field(None, gt=0)
    difficulty_level: int = Field(default=1, ge=1, le=5)
    is_public: bool = False
    is_reusable: bool = True
    tags: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)


class ActivityTemplateCreate(ActivityTemplateBase):
    created_by: UUID


class ActivityTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    template_data: Optional[Dict[str, Any]] = None
    default_settings: Optional[Dict[str, Any]] = None
    estimated_duration_minutes: Optional[int] = Field(None, gt=0)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    is_public: Optional[bool] = None
    is_reusable: Optional[bool] = None
    tags: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None


class ActivityTemplateResponse(ActivityTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    usage_count: int
    rating: Optional[float] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# Activity Schemas
class ActivityBase(BaseModel):
    template_id: Optional[UUID] = None
    title: str = Field(max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    activity_type: str = Field(pattern="^(video|quiz|assignment|discussion|simulation|reading|project)$")
    content: Dict[str, Any]
    estimated_duration_minutes: Optional[int] = Field(None, gt=0)
    max_score: Optional[float] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, gt=0)
    is_mandatory: bool = True
    is_graded: bool = False
    allow_multiple_attempts: bool = True
    max_attempts: Optional[int] = Field(None, ge=1)
    settings: Dict[str, Any] = Field(default_factory=dict)
    resources: List[Dict[str, Any]] = Field(default_factory=list)


class ActivityCreate(ActivityBase):
    created_by: UUID
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    estimated_duration_minutes: Optional[int] = Field(None, gt=0)
    max_score: Optional[float] = Field(None, gt=0)
    passing_score: Optional[float] = Field(None, gt=0)
    is_mandatory: Optional[bool] = None
    is_graded: Optional[bool] = None
    allow_multiple_attempts: Optional[bool] = None
    max_attempts: Optional[int] = Field(None, ge=1)
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    resources: Optional[List[Dict[str, Any]]] = None


class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# Course Activity Schemas
class CourseActivityBase(BaseModel):
    course_id: UUID
    module_id: Optional[UUID] = None
    activity_id: UUID
    order_sequence: int = Field(ge=1)
    title_override: Optional[str] = Field(None, max_length=255)
    description_override: Optional[str] = None
    settings_override: Dict[str, Any] = Field(default_factory=dict)
    weight_in_grade: float = Field(default=1.0, gt=0)
    is_required: bool = True


class CourseActivityCreate(CourseActivityBase):
    available_from_override: Optional[datetime] = None
    available_until_override: Optional[datetime] = None


class CourseActivityResponse(CourseActivityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    available_from_override: Optional[datetime] = None
    available_until_override: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None