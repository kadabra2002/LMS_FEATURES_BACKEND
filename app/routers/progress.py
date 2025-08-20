from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.progress import (
    ProgressTrackingCreate, ProgressTrackingUpdate, ProgressTrackingResponse,
    UserAssessmentCreate, UserAssessmentUpdate, UserAssessmentResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceResponse
)
from app.services.progress import ProgressService

router = APIRouter()


@router.post("/tracking", response_model=ProgressTrackingResponse)
async def create_progress_tracking(
    progress_data: ProgressTrackingCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new progress tracking record."""
    service = ProgressService(db)
    return await service.create_progress_tracking(progress_data)


@router.get("/tracking/{progress_id}", response_model=ProgressTrackingResponse)
async def get_progress_tracking(
    progress_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get progress tracking by ID."""
    service = ProgressService(db)
    progress = await service.get_progress_tracking(progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress tracking not found")
    return progress


@router.get("/tracking/user/{user_id}", response_model=List[ProgressTrackingResponse])
async def get_user_progress(
    user_id: UUID,
    course_id: Optional[UUID] = Query(None),
    module_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get user's progress tracking records."""
    service = ProgressService(db)
    return await service.get_user_progress(
        user_id=user_id,
        course_id=course_id,
        module_id=module_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get("/tracking/course/{course_id}", response_model=List[ProgressTrackingResponse])
async def get_course_progress(
    course_id: UUID,
    user_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get progress tracking records for a course."""
    service = ProgressService(db)
    return await service.get_course_progress(
        course_id=course_id,
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.put("/tracking/{progress_id}", response_model=ProgressTrackingResponse)
async def update_progress_tracking(
    progress_id: UUID,
    progress_data: ProgressTrackingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update progress tracking record."""
    service = ProgressService(db)
    progress = await service.update_progress_tracking(progress_id, progress_data)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress tracking not found")
    return progress


@router.delete("/tracking/{progress_id}")
async def delete_progress_tracking(
    progress_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete progress tracking record."""
    service = ProgressService(db)
    success = await service.delete_progress_tracking(progress_id)
    if not success:
        raise HTTPException(status_code=404, detail="Progress tracking not found")
    return {"message": "Progress tracking deleted successfully"}


# User Assessment Endpoints
@router.post("/assessments", response_model=UserAssessmentResponse)
async def create_user_assessment(
    assessment_data: UserAssessmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user assessment record."""
    service = ProgressService(db)
    return await service.create_user_assessment(assessment_data)


@router.get("/assessments/{assessment_id}", response_model=UserAssessmentResponse)
async def get_user_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user assessment by ID."""
    service = ProgressService(db)
    assessment = await service.get_user_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="User assessment not found")
    return assessment


@router.get("/assessments/user/{user_id}", response_model=List[UserAssessmentResponse])
async def get_user_assessments(
    user_id: UUID,
    assessment_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get user's assessment records."""
    service = ProgressService(db)
    return await service.get_user_assessments(
        user_id=user_id,
        assessment_id=assessment_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.put("/assessments/{assessment_id}", response_model=UserAssessmentResponse)
async def update_user_assessment(
    assessment_id: UUID,
    assessment_data: UserAssessmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user assessment record."""
    service = ProgressService(db)
    assessment = await service.update_user_assessment(assessment_id, assessment_data)
    if not assessment:
        raise HTTPException(status_code=404, detail="User assessment not found")
    return assessment


# Attendance Endpoints
@router.post("/attendance", response_model=AttendanceResponse)
async def create_attendance(
    attendance_data: AttendanceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new attendance record."""
    service = ProgressService(db)
    return await service.create_attendance(attendance_data)


@router.get("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get attendance by ID."""
    service = ProgressService(db)
    attendance = await service.get_attendance(attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


@router.get("/attendance/user/{user_id}", response_model=List[AttendanceResponse])
async def get_user_attendance(
    user_id: UUID,
    course_id: Optional[UUID] = Query(None),
    session_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get user's attendance records."""
    service = ProgressService(db)
    return await service.get_user_attendance(
        user_id=user_id,
        course_id=course_id,
        session_id=session_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: UUID,
    attendance_data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update attendance record."""
    service = ProgressService(db)
    attendance = await service.update_attendance(attendance_id, attendance_data)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    return attendance


@router.get("/analytics/user/{user_id}/summary")
async def get_user_progress_summary(
    user_id: UUID,
    course_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive progress summary for a user."""
    service = ProgressService(db)
    return await service.get_user_progress_summary(user_id, course_id)


@router.get("/analytics/course/{course_id}/summary")
async def get_course_progress_summary(
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive progress summary for a course."""
    service = ProgressService(db)
    return await service.get_course_progress_summary(course_id)