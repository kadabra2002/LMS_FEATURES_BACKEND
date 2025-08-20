from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.models.automation import AutomationRule, AutomationExecution, AutomationLog
from app.schemas.automation import (
    AutomationRuleCreate, AutomationRuleUpdate
)


class AutomationService:
    """Service for managing automation rules and executions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Automation Rule Methods
    async def create_automation_rule(self, rule_data: AutomationRuleCreate) -> AutomationRule:
        """Create a new automation rule."""
        rule = AutomationRule(**rule_data.model_dump())
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule
    
    async def get_automation_rule(self, rule_id: UUID) -> Optional[AutomationRule]:
        """Get automation rule by ID."""
        result = await self.db.execute(
            select(AutomationRule)
            .options(selectinload(AutomationRule.execution_logs))
            .where(AutomationRule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_automation_rules(
        self,
        trigger_type: Optional[str] = None,
        action_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        created_by: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AutomationRule]:
        """Get automation rules with optional filters."""
        query = select(AutomationRule)
        
        if trigger_type:
            query = query.where(AutomationRule.trigger_type == trigger_type)
        if action_type:
            query = query.where(AutomationRule.action_type == action_type)
        if is_active is not None:
            query = query.where(AutomationRule.is_active == is_active)
        if created_by:
            query = query.where(AutomationRule.created_by == created_by)
        
        query = query.offset(skip).limit(limit).order_by(AutomationRule.priority.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_automation_rule(
        self,
        rule_id: UUID,
        rule_data: AutomationRuleUpdate
    ) -> Optional[AutomationRule]:
        """Update automation rule."""
        existing = await self.get_automation_rule(rule_id)
        if not existing:
            return None
        
        update_data = rule_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(AutomationRule)
            .where(AutomationRule.id == rule_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_automation_rule(rule_id)
    
    async def delete_automation_rule(self, rule_id: UUID) -> bool:
        """Delete automation rule and related executions."""
        result = await self.db.execute(
            delete(AutomationRule).where(AutomationRule.id == rule_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def activate_rule(self, rule_id: UUID) -> bool:
        """Activate an automation rule."""
        result = await self.db.execute(
            update(AutomationRule)
            .where(AutomationRule.id == rule_id)
            .values(is_active=True)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def deactivate_rule(self, rule_id: UUID) -> bool:
        """Deactivate an automation rule."""
        result = await self.db.execute(
            update(AutomationRule)
            .where(AutomationRule.id == rule_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Automation Execution Methods
    async def create_execution(
        self,
        rule_id: UUID,
        trigger_data: Dict[str, Any],
        execution_context: Dict[str, Any] = None
    ) -> AutomationExecution:
        """Create a new automation execution."""
        execution = AutomationExecution(
            rule_id=rule_id,
            trigger_data=trigger_data,
            execution_context=execution_context or {}
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        return execution
    
    async def get_execution(self, execution_id: UUID) -> Optional[AutomationExecution]:
        """Get automation execution by ID."""
        result = await self.db.execute(
            select(AutomationExecution).where(AutomationExecution.id == execution_id)
        )
        return result.scalar_one_or_none()
    
    async def get_rule_executions(
        self,
        rule_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AutomationExecution]:
        """Get executions for a specific rule."""
        query = select(AutomationExecution).where(AutomationExecution.rule_id == rule_id)
        
        if status:
            query = query.where(AutomationExecution.status == status)
        
        query = query.offset(skip).limit(limit).order_by(AutomationExecution.started_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_execution_status(
        self,
        execution_id: UUID,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        affected_users_count: int = 0
    ) -> bool:
        """Update execution status and result."""
        update_data = {
            "status": status,
            "affected_users_count": affected_users_count
        }
        
        if status in ["completed", "failed", "cancelled"]:
            update_data["completed_at"] = datetime.utcnow()
        
        if result:
            update_data["result"] = result
        
        if error_message:
            update_data["error_message"] = error_message
        
        result = await self.db.execute(
            update(AutomationExecution)
            .where(AutomationExecution.id == execution_id)
            .values(**update_data)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Automation Log Methods
    async def create_log(
        self,
        rule_id: UUID,
        log_level: str,
        message: str,
        execution_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        course_id: Optional[UUID] = None,
        additional_data: Dict[str, Any] = None
    ) -> AutomationLog:
        """Create a new automation log entry."""
        log = AutomationLog(
            rule_id=rule_id,
            execution_id=execution_id,
            log_level=log_level,
            message=message,
            user_id=user_id,
            course_id=course_id,
            additional_data=additional_data or {}
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
    
    async def get_rule_logs(
        self,
        rule_id: UUID,
        log_level: Optional[str] = None,
        execution_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AutomationLog]:
        """Get logs for a specific rule."""
        query = select(AutomationLog).where(AutomationLog.rule_id == rule_id)
        
        if log_level:
            query = query.where(AutomationLog.log_level == log_level)
        if execution_id:
            query = query.where(AutomationLog.execution_id == execution_id)
        
        query = query.offset(skip).limit(limit).order_by(AutomationLog.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # Rule Execution Logic
    async def execute_rule(self, rule_id: UUID, trigger_data: Dict[str, Any]) -> Optional[AutomationExecution]:
        """Execute an automation rule."""
        rule = await self.get_automation_rule(rule_id)
        if not rule or not rule.is_active:
            return None
        
        # Check cooldown
        if rule.cooldown_minutes and rule.last_executed_at:
            cooldown_end = rule.last_executed_at + timedelta(minutes=rule.cooldown_minutes)
            if datetime.utcnow() < cooldown_end:
                await self.create_log(
                    rule_id=rule_id,
                    log_level="INFO",
                    message=f"Rule execution skipped due to cooldown period"
                )
                return None
        
        # Check max executions
        if rule.max_executions and rule.execution_count >= rule.max_executions:
            await self.create_log(
                rule_id=rule_id,
                log_level="INFO",
                message=f"Rule execution skipped - max executions ({rule.max_executions}) reached"
            )
            return None
        
        # Create execution record
        execution = await self.create_execution(rule_id, trigger_data)
        
        try:
            # Log execution start
            await self.create_log(
                rule_id=rule_id,
                execution_id=execution.id,
                log_level="INFO",
                message=f"Starting execution of rule '{rule.name}'"
            )
            
            # Execute the rule actions
            result = await self._execute_rule_actions(rule, trigger_data, execution.id)
            
            # Update execution as completed
            await self.update_execution_status(
                execution.id,
                "completed",
                result=result,
                affected_users_count=result.get("affected_users", 0)
            )
            
            # Update rule execution count and last executed time
            await self.db.execute(
                update(AutomationRule)
                .where(AutomationRule.id == rule_id)
                .values(
                    execution_count=AutomationRule.execution_count + 1,
                    last_executed_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            
            await self.create_log(
                rule_id=rule_id,
                execution_id=execution.id,
                log_level="INFO",
                message=f"Rule execution completed successfully"
            )
            
        except Exception as e:
            # Update execution as failed
            await self.update_execution_status(
                execution.id,
                "failed",
                error_message=str(e)
            )
            
            await self.create_log(
                rule_id=rule_id,
                execution_id=execution.id,
                log_level="ERROR",
                message=f"Rule execution failed: {str(e)}"
            )
        
        return execution
    
    async def _execute_rule_actions(
        self,
        rule: AutomationRule,
        trigger_data: Dict[str, Any],
        execution_id: UUID
    ) -> Dict[str, Any]:
        """Execute the actions defined in an automation rule."""
        result = {"actions_executed": [], "affected_users": 0}
        
        for action in rule.actions:
            action_type = action.get("type")
            action_config = action.get("config", {})
            
            if action_type == "email":
                # Execute email action
                email_result = await self._execute_email_action(
                    action_config, trigger_data, rule.id, execution_id
                )
                result["actions_executed"].append({
                    "type": "email",
                    "result": email_result
                })
                result["affected_users"] += email_result.get("recipients_count", 0)
            
            elif action_type == "notification":
                # Execute notification action
                notification_result = await self._execute_notification_action(
                    action_config, trigger_data, rule.id, execution_id
                )
                result["actions_executed"].append({
                    "type": "notification",
                    "result": notification_result
                })
                result["affected_users"] += notification_result.get("recipients_count", 0)
            
            elif action_type == "enrollment":
                # Execute enrollment action
                enrollment_result = await self._execute_enrollment_action(
                    action_config, trigger_data, rule.id, execution_id
                )
                result["actions_executed"].append({
                    "type": "enrollment",
                    "result": enrollment_result
                })
                result["affected_users"] += enrollment_result.get("enrolled_count", 0)
        
        return result
    
    async def _execute_email_action(
        self,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any],
        rule_id: UUID,
        execution_id: UUID
    ) -> Dict[str, Any]:
        """Execute email action (placeholder implementation)."""
        # This would integrate with your email service
        await self.create_log(
            rule_id=rule_id,
            execution_id=execution_id,
            log_level="INFO",
            message=f"Email action executed with config: {config}"
        )
        
        return {
            "status": "sent",
            "recipients_count": config.get("recipient_count", 1),
            "subject": config.get("subject", "Automated notification")
        }
    
    async def _execute_notification_action(
        self,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any],
        rule_id: UUID,
        execution_id: UUID
    ) -> Dict[str, Any]:
        """Execute notification action (placeholder implementation)."""
        # This would integrate with your notification service
        await self.create_log(
            rule_id=rule_id,
            execution_id=execution_id,
            log_level="INFO",
            message=f"Notification action executed with config: {config}"
        )
        
        return {
            "status": "sent",
            "recipients_count": config.get("recipient_count", 1),
            "notification_type": config.get("type", "in_app")
        }
    
    async def _execute_enrollment_action(
        self,
        config: Dict[str, Any],
        trigger_data: Dict[str, Any],
        rule_id: UUID,
        execution_id: UUID
    ) -> Dict[str, Any]:
        """Execute enrollment action (placeholder implementation)."""
        # This would integrate with your enrollment service
        await self.create_log(
            rule_id=rule_id,
            execution_id=execution_id,
            log_level="INFO",
            message=f"Enrollment action executed with config: {config}"
        )
        
        return {
            "status": "completed",
            "enrolled_count": config.get("user_count", 1),
            "course_id": config.get("course_id")
        }
    
    # Analytics
    async def get_automation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive automation analytics."""
        # Get rule statistics
        result = await self.db.execute(select(AutomationRule))
        rules = result.scalars().all()
        
        total_rules = len(rules)
        active_rules = len([r for r in rules if r.is_active])
        
        # Get execution statistics
        result = await self.db.execute(select(AutomationExecution))
        executions = result.scalars().all()
        
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == "completed"])
        failed_executions = len([e for e in executions if e.status == "failed"])
        
        # Calculate success rate
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Rule type breakdown
        rule_types = {}
        for rule in rules:
            rule_type = rule.trigger_type
            rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
        
        return {
            "rule_stats": {
                "total_rules": total_rules,
                "active_rules": active_rules,
                "inactive_rules": total_rules - active_rules
            },
            "execution_stats": {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": round(success_rate, 2)
            },
            "rule_type_breakdown": rule_types,
            "total_users_affected": sum(e.affected_users_count for e in executions)
        }