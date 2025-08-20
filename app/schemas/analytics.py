from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AnalyticsDataBase(BaseModel):
    user_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    metric_type: str = Field(max_length=100)
    metric_category: str = Field(max_length=50, pattern="^(engagement|performance|progress|behavior|system)$")
    value: Optional[float] = None
    string_value: Optional[str] = Field(None, max_length=255)
    json_value: Optional[Dict[str, Any]] = None
    page_url: Optional[str] = Field(None, max_length=500)
    user_agent: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=45)
    duration_seconds: Optional[int] = Field(None, ge=0)
    dimensions: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsDataCreate(AnalyticsDataBase):
    timestamp: Optional[datetime] = None


class AnalyticsDataResponse(AnalyticsDataBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    timestamp: datetime
    batch_id: Optional[UUID] = None
    processed_at: Optional[datetime] = None


# User Metrics Schemas
class UserMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    date: datetime
    period_type: str
    total_sessions: int
    total_time_minutes: int
    courses_accessed: int
    activities_completed: int
    average_score: Optional[float] = None
    assessments_passed: int
    assessments_failed: int
    certificates_earned: int
    courses_started: int
    courses_completed: int
    modules_completed: int
    forum_posts: int
    discussions_participated: int
    peer_interactions: int
    custom_metrics: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None


# Report Schemas
class ReportBase(BaseModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    report_type: str = Field(pattern="^(performance|engagement|progress|compliance|custom)$")
    report_category: str = Field(pattern="^(user|course|system|custom)$")
    parameters: Dict[str, Any]
    data_source: str = Field(max_length=100)
    is_scheduled: bool = False
    schedule_cron: Optional[str] = Field(None, max_length=100)
    is_public: bool = False
    allowed_roles: Optional[List[str]] = None
    allowed_users: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ReportCreate(ReportBase):
    created_by: UUID


class ReportUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_scheduled: Optional[bool] = None
    schedule_cron: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None
    allowed_roles: Optional[List[str]] = None
    allowed_users: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ReportResponse(ReportBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    last_generated_at: Optional[datetime] = None
    generation_status: str
    file_path: Optional[str] = None
    file_format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# Analytics Query Schemas
class AnalyticsQuery(BaseModel):
    start_date: datetime
    end_date: datetime
    metric_types: Optional[List[str]] = None
    user_ids: Optional[List[UUID]] = None
    course_ids: Optional[List[UUID]] = None
    group_by: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = Field(None, gt=0, le=1000)
    offset: Optional[int] = Field(None, ge=0)


class AnalyticsAggregation(BaseModel):
    metric_type: str
    aggregation_function: str = Field(pattern="^(sum|avg|count|min|max)$")
    group_by: Optional[str] = None
    value: float
    count: int
    period: Optional[str] = None