from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.models.target import Target, Reminder
from app.schemas.target import (
    TargetCreate, TargetUpdate,
    ReminderCreate, ReminderUpdate
)


class TargetService:
    """Service for managing targets and reminders."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Target Methods
    async def create_target(self, target_data: TargetCreate) -> Target:
        """Create a new target."""
        target = Target(**target_data.model_dump())
        self.db.add(target)
        await self.db.commit()
        await self.db.refresh(target)
        return target
    
    async def get_target(self, target_id: UUID) -> Optional[Target]:
        """Get target by ID with related reminders."""
        result = await self.db.execute(
            select(Target)
            .options(selectinload(Target.reminders))
            .where(Target.id == target_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_targets(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        target_type: Optional[str] = None,
        priority: Optional[str] = None,
        course_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Target]:
        """Get user's targets with optional filters."""
        query = select(Target).where(Target.user_id == user_id)
        
        if status:
            query = query.where(Target.status == status)
        if target_type:
            query = query.where(Target.target_type == target_type)
        if priority:
            query = query.where(Target.priority == priority)
        if course_id:
            query = query.where(Target.course_id == course_id)
        
        query = query.offset(skip).limit(limit).order_by(Target.deadline.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_target(
        self,
        target_id: UUID,
        target_data: TargetUpdate
    ) -> Optional[Target]:
        """Update target."""
        existing = await self.get_target(target_id)
        if not existing:
            return None
        
        update_data = target_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Target)
            .where(Target.id == target_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_target(target_id)
    
    async def delete_target(self, target_id: UUID) -> bool:
        """Delete target and related reminders."""
        result = await self.db.execute(
            delete(Target).where(Target.id == target_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_overdue_targets(
        self,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Target]:
        """Get overdue targets."""
        query = select(Target).where(
            and_(
                Target.deadline < datetime.utcnow(),
                Target.status.in_(["active", "in_progress"])
            )
        )
        
        if user_id:
            query = query.where(Target.user_id == user_id)
        
        query = query.offset(skip).limit(limit).order_by(Target.deadline.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_upcoming_targets(
        self,
        user_id: UUID,
        days_ahead: int = 7,
        skip: int = 0,
        limit: int = 100
    ) -> List[Target]:
        """Get targets due within specified days."""
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = select(Target).where(
            and_(
                Target.user_id == user_id,
                Target.deadline <= future_date,
                Target.deadline >= datetime.utcnow(),
                Target.status.in_(["active", "in_progress"])
            )
        )
        
        query = query.offset(skip).limit(limit).order_by(Target.deadline.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # Reminder Methods
    async def create_reminder(self, reminder_data: ReminderCreate) -> Reminder:
        """Create a new reminder."""
        reminder = Reminder(**reminder_data.model_dump())
        self.db.add(reminder)
        await self.db.commit()
        await self.db.refresh(reminder)
        return reminder
    
    async def get_reminder(self, reminder_id: UUID) -> Optional[Reminder]:
        """Get reminder by ID."""
        result = await self.db.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        return result.scalar_one_or_none()
    
    async def get_target_reminders(
        self,
        target_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reminder]:
        """Get reminders for a target."""
        query = select(Reminder).where(Reminder.target_id == target_id)
        
        if status:
            query = query.where(Reminder.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Reminder.reminder_time.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_reminder(
        self,
        reminder_id: UUID,
        reminder_data: ReminderUpdate
    ) -> Optional[Reminder]:
        """Update reminder."""
        existing = await self.get_reminder(reminder_id)
        if not existing:
            return None
        
        update_data = reminder_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Reminder)
            .where(Reminder.id == reminder_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_reminder(reminder_id)
    
    async def delete_reminder(self, reminder_id: UUID) -> bool:
        """Delete reminder."""
        result = await self.db.execute(
            delete(Reminder).where(Reminder.id == reminder_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_pending_reminders(
        self,
        reminder_time_before: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Reminder]:
        """Get pending reminders that need to be sent."""
        if reminder_time_before is None:
            reminder_time_before = datetime.utcnow()
        
        query = select(Reminder).where(
            and_(
                Reminder.reminder_time <= reminder_time_before,
                Reminder.status == "scheduled",
                Reminder.is_sent == False
            )
        )
        
        query = query.offset(skip).limit(limit).order_by(Reminder.reminder_time.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_reminder_sent(self, reminder_id: UUID) -> bool:
        """Mark reminder as sent."""
        result = await self.db.execute(
            update(Reminder)
            .where(Reminder.id == reminder_id)
            .values(
                is_sent=True,
                sent_at=datetime.utcnow(),
                status="sent"
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Target Analytics
    async def get_user_target_summary(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive target summary for a user."""
        # Get all targets for the user
        result = await self.db.execute(
            select(Target).where(Target.user_id == user_id)
        )
        targets = result.scalars().all()
        
        total_targets = len(targets)
        completed_targets = len([t for t in targets if t.status == "completed"])
        active_targets = len([t for t in targets if t.status == "active"])
        overdue_targets = len([t for t in targets if t.deadline < datetime.utcnow() and t.status in ["active", "in_progress"]])
        
        # Calculate completion rate
        completion_rate = (completed_targets / total_targets * 100) if total_targets > 0 else 0
        
        # Get targets by priority
        priority_breakdown = {
            "critical": len([t for t in targets if t.priority == "critical"]),
            "high": len([t for t in targets if t.priority == "high"]),
            "medium": len([t for t in targets if t.priority == "medium"]),
            "low": len([t for t in targets if t.priority == "low"])
        }
        
        # Get targets by type
        type_breakdown = {}
        for target in targets:
            target_type = target.target_type
            type_breakdown[target_type] = type_breakdown.get(target_type, 0) + 1
        
        return {
            "user_id": str(user_id),
            "overview": {
                "total_targets": total_targets,
                "completed_targets": completed_targets,
                "active_targets": active_targets,
                "overdue_targets": overdue_targets,
                "completion_rate": round(completion_rate, 2)
            },
            "priority_breakdown": priority_breakdown,
            "type_breakdown": type_breakdown,
            "upcoming_deadlines": len(await self.get_upcoming_targets(user_id, days_ahead=7))
        }
    
    async def auto_create_reminders_for_target(self, target_id: UUID) -> List[Reminder]:
        """Automatically create reminders for a target based on its deadline."""
        target = await self.get_target(target_id)
        if not target:
            return []
        
        reminders = []
        
        # Create reminders at different intervals before the deadline
        reminder_intervals = [
            {"days": 7, "title": "One week reminder"},
            {"days": 3, "title": "Three days reminder"},
            {"days": 1, "title": "One day reminder"},
            {"hours": 2, "title": "Final reminder"}
        ]
        
        for interval in reminder_intervals:
            if "days" in interval:
                reminder_time = target.deadline - timedelta(days=interval["days"])
            else:
                reminder_time = target.deadline - timedelta(hours=interval["hours"])
            
            # Only create reminder if it's in the future
            if reminder_time > datetime.utcnow():
                reminder_data = ReminderCreate(
                    target_id=target_id,
                    reminder_type="email",
                    reminder_time=reminder_time,
                    title=f"{interval['title']}: {target.title}",
                    message=f"This is a reminder that your target '{target.title}' is due on {target.deadline.strftime('%Y-%m-%d %H:%M')}."
                )
                
                reminder = await self.create_reminder(reminder_data)
                reminders.append(reminder)
        
        return reminders