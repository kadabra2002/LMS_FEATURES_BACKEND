from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.target import (
    TargetCreate, TargetUpdate, TargetResponse,
    ReminderCreate, ReminderUpdate, ReminderResponse
)
from app.services.target import TargetService

router = APIRouter()


# Target Endpoints
@router.post("/", response_model=TargetResponse)
async def create_target(
    target_data: TargetCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new target."""
    service = TargetService(db)
    return await service.create_target(target_data)


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get target by ID."""
    service = TargetService(db)
    target = await service.get_target(target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@router.get("/user/{user_id}", response_model=List[TargetResponse])
async def get_user_targets(
    user_id: UUID,
    status: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    course_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get user's targets with optional filters."""
    service = TargetService(db)
    return await service.get_user_targets(
        user_id=user_id,
        status=status,
        target_type=target_type,
        priority=priority,
        course_id=course_id,
        skip=skip,
        limit=limit
    )


@router.put("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: UUID,
    target_data: TargetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update target."""
    service = TargetService(db)
    target = await service.update_target(target_id, target_data)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@router.delete("/{target_id}")
async def delete_target(
    target_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete target."""
    service = TargetService(db)
    success = await service.delete_target(target_id)
    if not success:
        raise HTTPException(status_code=404, detail="Target not found")
    return {"message": "Target deleted successfully"}


@router.get("/overdue", response_model=List[TargetResponse])
async def get_overdue_targets(
    user_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get overdue targets."""
    service = TargetService(db)
    return await service.get_overdue_targets(
        user_id=user_id,
        skip=skip,
        limit=limit
    )


@router.get("/user/{user_id}/upcoming", response_model=List[TargetResponse])
async def get_upcoming_targets(
    user_id: UUID,
    days_ahead: int = Query(7, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get targets due within specified days."""
    service = TargetService(db)
    return await service.get_upcoming_targets(
        user_id=user_id,
        days_ahead=days_ahead,
        skip=skip,
        limit=limit
    )


# Reminder Endpoints
@router.post("/{target_id}/reminders", response_model=ReminderResponse)
async def create_reminder(
    target_id: UUID,
    reminder_data: ReminderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new reminder for a target."""
    if reminder_data.target_id != target_id:
        raise HTTPException(status_code=400, detail="Target ID mismatch")
    
    service = TargetService(db)
    return await service.create_reminder(reminder_data)


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get reminder by ID."""
    service = TargetService(db)
    reminder = await service.get_reminder(reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.get("/{target_id}/reminders", response_model=List[ReminderResponse])
async def get_target_reminders(
    target_id: UUID,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get reminders for a target."""
    service = TargetService(db)
    return await service.get_target_reminders(
        target_id=target_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    reminder_data: ReminderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update reminder."""
    service = TargetService(db)
    reminder = await service.update_reminder(reminder_id, reminder_data)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete reminder."""
    service = TargetService(db)
    success = await service.delete_reminder(reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted successfully"}


@router.get("/reminders/pending", response_model=List[ReminderResponse])
async def get_pending_reminders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get pending reminders that need to be sent."""
    service = TargetService(db)
    return await service.get_pending_reminders(skip=skip, limit=limit)


@router.post("/reminders/{reminder_id}/mark-sent")
async def mark_reminder_sent(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Mark reminder as sent."""
    service = TargetService(db)
    success = await service.mark_reminder_sent(reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder marked as sent"}


@router.get("/user/{user_id}/summary")
async def get_user_target_summary(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive target summary for a user."""
    service = TargetService(db)
    return await service.get_user_target_summary(user_id)


@router.post("/{target_id}/auto-reminders", response_model=List[ReminderResponse])
async def auto_create_reminders_for_target(
    target_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Automatically create reminders for a target based on its deadline."""
    service = TargetService(db)
    reminders = await service.auto_create_reminders_for_target(target_id)
    return reminders