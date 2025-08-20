from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AutomationRuleBase(BaseModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    trigger_type: str = Field(pattern="^(user_enrollment|course_completion|deadline_approaching|assessment_failed|inactivity|target_overdue)$")
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    action_type: str = Field(pattern="^(email|notification|enrollment|reminder|report|escalation)$")
    is_active: bool = True
    priority: int = Field(default=1, ge=1, le=10)
    schedule_type: str = Field(default="immediate", pattern="^(immediate|scheduled|recurring)$")
    schedule_data: Optional[Dict[str, Any]] = None
    target_filters: Dict[str, Any] = Field(default_factory=dict)
    course_filters: Dict[str, Any] = Field(default_factory=dict)
    max_executions: Optional[int] = Field(None, gt=0)
    cooldown_minutes: Optional[int] = Field(None, gt=0)


class AutomationRuleCreate(AutomationRuleBase):
    created_by: UUID


class AutomationRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    action_type: Optional[str] = Field(None, pattern="^(email|notification|enrollment|reminder|report|escalation)$")
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    schedule_type: Optional[str] = Field(None, pattern="^(immediate|scheduled|recurring)$")
    schedule_data: Optional[Dict[str, Any]] = None
    target_filters: Optional[Dict[str, Any]] = None
    course_filters: Optional[Dict[str, Any]] = None
    max_executions: Optional[int] = Field(None, gt=0)
    cooldown_minutes: Optional[int] = Field(None, gt=0)


class AutomationRuleResponse(AutomationRuleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    execution_count: int
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_executed_at: Optional[datetime] = None


# Automation Execution Schemas
class AutomationExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    rule_id: UUID
    trigger_data: Dict[str, Any]
    execution_context: Dict[str, Any]
    status: str
    result: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    execution_time_ms: Optional[int] = None
    affected_users_count: int


# Automation Log Schemas
class AutomationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    execution_id: Optional[UUID] = None
    rule_id: UUID
    log_level: str
    message: str
    user_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    additional_data: Dict[str, Any]
    created_at: datetime