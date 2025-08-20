from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.schemas.automation import (
    AutomationRuleCreate, AutomationRuleUpdate, AutomationRuleResponse,
    AutomationExecutionResponse, AutomationLogResponse
)
from app.services.automation import AutomationService

router = APIRouter()


# Automation Rule Endpoints
@router.post("/rules", response_model=AutomationRuleResponse)
async def create_automation_rule(
    rule_data: AutomationRuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new automation rule."""
    service = AutomationService(db)
    return await service.create_automation_rule(rule_data)


@router.get("/rules/{rule_id}", response_model=AutomationRuleResponse)
async def get_automation_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get automation rule by ID."""
    service = AutomationService(db)
    rule = await service.get_automation_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return rule


@router.get("/rules", response_model=List[AutomationRuleResponse])
async def get_automation_rules(
    trigger_type: Optional[str] = Query(None),
    action_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    created_by: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get automation rules with optional filters."""
    service = AutomationService(db)
    return await service.get_automation_rules(
        trigger_type=trigger_type,
        action_type=action_type,
        is_active=is_active,
        created_by=created_by,
        skip=skip,
        limit=limit
    )


@router.put("/rules/{rule_id}", response_model=AutomationRuleResponse)
async def update_automation_rule(
    rule_id: UUID,
    rule_data: AutomationRuleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update automation rule."""
    service = AutomationService(db)
    rule = await service.update_automation_rule(rule_id, rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return rule


@router.delete("/rules/{rule_id}")
async def delete_automation_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete automation rule."""
    service = AutomationService(db)
    success = await service.delete_automation_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return {"message": "Automation rule deleted successfully"}


@router.post("/rules/{rule_id}/activate")
async def activate_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Activate an automation rule."""
    service = AutomationService(db)
    success = await service.activate_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return {"message": "Automation rule activated"}


@router.post("/rules/{rule_id}/deactivate")
async def deactivate_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate an automation rule."""
    service = AutomationService(db)
    success = await service.deactivate_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Automation rule not found")
    return {"message": "Automation rule deactivated"}


# Automation Execution Endpoints
@router.post("/rules/{rule_id}/execute")
async def execute_rule(
    rule_id: UUID,
    trigger_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Execute an automation rule."""
    service = AutomationService(db)
    execution = await service.execute_rule(rule_id, trigger_data)
    if not execution:
        raise HTTPException(status_code=400, detail="Rule execution failed or skipped")
    return {"message": "Rule execution started", "execution_id": str(execution.id)}


@router.get("/executions/{execution_id}", response_model=AutomationExecutionResponse)
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get automation execution by ID."""
    service = AutomationService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/rules/{rule_id}/executions", response_model=List[AutomationExecutionResponse])
async def get_rule_executions(
    rule_id: UUID,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get executions for a specific rule."""
    service = AutomationService(db)
    return await service.get_rule_executions(
        rule_id=rule_id,
        status=status,
        skip=skip,
        limit=limit
    )


# Automation Log Endpoints
@router.get("/rules/{rule_id}/logs", response_model=List[AutomationLogResponse])
async def get_rule_logs(
    rule_id: UUID,
    log_level: Optional[str] = Query(None),
    execution_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get logs for a specific rule."""
    service = AutomationService(db)
    return await service.get_rule_logs(
        rule_id=rule_id,
        log_level=log_level,
        execution_id=execution_id,
        skip=skip,
        limit=limit
    )


@router.get("/analytics")
async def get_automation_analytics(
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive automation analytics."""
    service = AutomationService(db)
    return await service.get_automation_analytics()