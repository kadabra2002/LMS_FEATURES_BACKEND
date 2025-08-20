from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class AnalyticsData(BaseModel):
    __tablename__ = "analytics_data"
    
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    course_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    metric_type = Column(String(100), nullable=False, index=True)  # page_view, quiz_attempt, video_watch, etc.
    metric_category = Column(String(50), nullable=False)  # engagement, performance, progress, etc.
    
    value = Column(Float, nullable=True)  # Numeric value
    string_value = Column(String(255), nullable=True)  # Text value
    json_value = Column(JSON, nullable=True)  # Complex data
    
    # Contextual information
    page_url = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Dimensions for filtering and grouping
    dimensions = Column(JSON, default=dict)  # Additional dimensions for analysis
    
    # Batch processing
    batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)


class UserMetrics(BaseModel):
    __tablename__ = "user_metrics"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Time period
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(10), nullable=False)  # daily, weekly, monthly
    
    # Engagement metrics
    total_sessions = Column(Integer, default=0)
    total_time_minutes = Column(Integer, default=0)
    courses_accessed = Column(Integer, default=0)
    activities_completed = Column(Integer, default=0)
    
    # Performance metrics
    average_score = Column(Float, nullable=True)
    assessments_passed = Column(Integer, default=0)
    assessments_failed = Column(Integer, default=0)
    certificates_earned = Column(Integer, default=0)
    
    # Learning metrics
    courses_started = Column(Integer, default=0)
    courses_completed = Column(Integer, default=0)
    modules_completed = Column(Integer, default=0)
    
    # Interaction metrics
    forum_posts = Column(Integer, default=0)
    discussions_participated = Column(Integer, default=0)
    peer_interactions = Column(Integer, default=0)
    
    # Additional metrics
    custom_metrics = Column(JSON, default=dict)


class Report(BaseModel):
    __tablename__ = "reports"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    report_type = Column(String(50), nullable=False)  # performance, engagement, progress, compliance
    report_category = Column(String(50), nullable=False)  # user, course, system, custom
    
    # Configuration
    parameters = Column(JSON, nullable=False)  # Report parameters and filters
    data_source = Column(String(100), nullable=False)  # Source of the data
    
    # Scheduling
    is_scheduled = Column(Boolean, default=False)
    schedule_cron = Column(String(100), nullable=True)  # Cron expression for scheduling
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(ARRAY(String), nullable=True)
    allowed_users = Column(ARRAY(String), nullable=True)
    
    # Generation info
    last_generated_at = Column(DateTime(timezone=True), nullable=True)
    generation_status = Column(String(20), default="pending")  # pending, generating, completed, failed
    
    file_path = Column(String(500), nullable=True)  # Path to generated report file
    file_format = Column(String(10), nullable=True)  # pdf, excel, csv
    file_size_bytes = Column(Integer, nullable=True)
    
    # Metadata
    tags = Column(ARRAY(String), nullable=True)
    custom_fields = Column(JSON, default=dict)
    
    created_by = Column(UUID(as_uuid=True), nullable=False)