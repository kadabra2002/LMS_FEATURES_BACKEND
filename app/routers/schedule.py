from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.schedule import (
    CourseScheduleCreate, CourseScheduleUpdate, CourseScheduleResponse,
    UserCourseEnrollmentCreate, UserCourseEnrollmentUpdate, UserCourseEnrollmentResponse
)
from app.services.schedule import ScheduleService

router = APIRouter()


# Course Schedule Endpoints
@router.post("/", response_model=CourseScheduleResponse)
async def create_course_schedule(
    schedule_data: CourseScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new course schedule."""
    service = ScheduleService(db)
    return await service.create_course_schedule(schedule_data)


@router.get("/{schedule_id}", response_model=CourseScheduleResponse)
async def get_course_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get course schedule by ID."""
    service = ScheduleService(db)
    schedule = await service.get_course_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Course schedule not found")
    return schedule


@router.get("/", response_model=List[CourseScheduleResponse])
async def get_course_schedules(
    course_id: Optional[UUID] = Query(None),
    schedule_type: Optional[str] = Query(None),
    delivery_mode: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_mandatory: Optional[bool] = Query(None),
    created_by: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get course schedules with optional filters."""
    service = ScheduleService(db)
    return await service.get_course_schedules(
        course_id=course_id,
        schedule_type=schedule_type,
        delivery_mode=delivery_mode,
        status=status,
        is_mandatory=is_mandatory,
        created_by=created_by,
        skip=skip,
        limit=limit
    )


@router.put("/{schedule_id}", response_model=CourseScheduleResponse)
async def update_course_schedule(
    schedule_id: UUID,
    schedule_data: CourseScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update course schedule."""
    service = ScheduleService(db)
    schedule = await service.update_course_schedule(schedule_id, schedule_data)
    if not schedule:
        raise HTTPException(status_code=404, detail="Course schedule not found")
    return schedule


@router.delete("/{schedule_id}")
async def delete_course_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete course schedule."""
    service = ScheduleService(db)
    success = await service.delete_course_schedule(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course schedule not found")
    return {"message": "Course schedule deleted successfully"}


# User Course Enrollment Endpoints
@router.post("/enrollments", response_model=UserCourseEnrollmentResponse)
async def create_enrollment(
    enrollment_data: UserCourseEnrollmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new course enrollment."""
    service = ScheduleService(db)
    try:
        return await service.create_enrollment(enrollment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/enrollments/{enrollment_id}", response_model=UserCourseEnrollmentResponse)
async def get_enrollment(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get enrollment by ID."""
    service = ScheduleService(db)
    enrollment = await service.get_enrollment(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.get("/users/{user_id}/enrollments", response_model=List[UserCourseEnrollmentResponse])
async def get_user_enrollments(
    user_id: UUID,
    status: Optional[str] = Query(None),
    course_id: Optional[UUID] = Query(None),
    enrollment_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get user's course enrollments."""
    service = ScheduleService(db)
    return await service.get_user_enrollments(
        user_id=user_id,
        status=status,
        course_id=course_id,
        enrollment_type=enrollment_type,
        skip=skip,
        limit=limit
    )


@router.get("/{schedule_id}/enrollments", response_model=List[UserCourseEnrollmentResponse])
async def get_schedule_enrollments(
    schedule_id: UUID,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get enrollments for a specific schedule."""
    service = ScheduleService(db)
    return await service.get_schedule_enrollments(
        schedule_id=schedule_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.put("/enrollments/{enrollment_id}", response_model=UserCourseEnrollmentResponse)
async def update_enrollment(
    enrollment_id: UUID,
    enrollment_data: UserCourseEnrollmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update course enrollment."""
    service = ScheduleService(db)
    enrollment = await service.update_enrollment(enrollment_id, enrollment_data)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.post("/enrollments/{enrollment_id}/cancel")
async def cancel_enrollment(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a course enrollment."""
    service = ScheduleService(db)
    success = await service.cancel_enrollment(enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"message": "Enrollment cancelled successfully"}


@router.get("/{schedule_id}/analytics")
async def get_schedule_analytics(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive analytics for a course schedule."""
    service = ScheduleService(db)
    return await service.get_schedule_analytics(schedule_id)


@router.get("/courses/{course_id}/available", response_model=List[CourseScheduleResponse])
async def get_available_schedules(
    course_id: UUID,
    user_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get available schedules for a course that a user can enroll in."""
    service = ScheduleService(db)
    return await service.get_available_schedules(course_id, user_id)