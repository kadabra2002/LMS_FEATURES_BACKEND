from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import BaseModel


class AutomationRule(BaseModel):
    __tablename__ = "automation_rules"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    trigger_type = Column(String(50), nullable=False)  # user_enrollment, course_completion, deadline_approaching, etc.
    trigger_conditions = Column(JSON, nullable=False)  # Conditions that activate the rule
    
    actions = Column(JSON, nullable=False)  # Actions to perform
    action_type = Column(String(50), nullable=False)  # email, notification, enrollment, etc.
    
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # Execution priority
    
    # Scheduling
    schedule_type = Column(String(20), default="immediate")  # immediate, scheduled, recurring
    schedule_data = Column(JSON, nullable=True)  # Schedule configuration
    
    # Filtering
    target_filters = Column(JSON, default=dict)  # Who this rule applies to
    course_filters = Column(JSON, default=dict)  # Which courses this applies to
    
    # Limits and controls
    max_executions = Column(Integer, nullable=True)  # Max times this can run
    execution_count = Column(Integer, default=0)
    cooldown_minutes = Column(Integer, nullable=True)  # Minimum time between executions
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    execution_logs = relationship("AutomationExecution", back_populates="rule")


class AutomationExecution(BaseModel):
    __tablename__ = "automation_executions"
    
    rule_id = Column(UUID(as_uuid=True), ForeignKey("automation_rules.id"), nullable=False)
    
    trigger_data = Column(JSON, nullable=False)  # Data that triggered the execution
    execution_context = Column(JSON, default=dict)  # Context at time of execution
    
    status = Column(String(20), default="running")  # running, completed, failed, cancelled
    result = Column(JSON, nullable=True)  # Execution result
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Performance metrics
    execution_time_ms = Column(Integer, nullable=True)
    affected_users_count = Column(Integer, default=0)
    
    # Relationships
    rule = relationship("AutomationRule", back_populates="execution_logs")


class AutomationLog(BaseModel):
    __tablename__ = "automation_logs"
    
    execution_id = Column(UUID(as_uuid=True), ForeignKey("automation_executions.id"), nullable=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("automation_rules.id"), nullable=False)
    
    log_level = Column(String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Affected user
    course_id = Column(UUID(as_uuid=True), nullable=True)  # Related course
    
    additional_data = Column(JSON, default=dict)