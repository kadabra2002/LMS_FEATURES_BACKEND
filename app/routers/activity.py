from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.database import get_db
from app.schemas.activity import (
    ActivityTemplateCreate, ActivityTemplateUpdate, ActivityTemplateResponse,
    ActivityCreate, ActivityUpdate, ActivityResponse,
    CourseActivityCreate, CourseActivityResponse
)
from app.services.activity import ActivityService

router = APIRouter()


# Activity Template Endpoints
@router.post("/templates", response_model=ActivityTemplateResponse)
async def create_activity_template(
    template_data: ActivityTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new activity template."""
    service = ActivityService(db)
    return await service.create_activity_template(template_data)


@router.get("/templates/{template_id}", response_model=ActivityTemplateResponse)
async def get_activity_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get activity template by ID."""
    service = ActivityService(db)
    template = await service.get_activity_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Activity template not found")
    return template


@router.get("/templates", response_model=List[ActivityTemplateResponse])
async def get_activity_templates(
    activity_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    is_reusable: Optional[bool] = Query(None),
    created_by: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get activity templates with optional filters."""
    service = ActivityService(db)
    return await service.get_activity_templates(
        activity_type=activity_type,
        category=category,
        is_public=is_public,
        is_reusable=is_reusable,
        created_by=created_by,
        search=search,
        skip=skip,
        limit=limit
    )


@router.put("/templates/{template_id}", response_model=ActivityTemplateResponse)
async def update_activity_template(
    template_id: UUID,
    template_data: ActivityTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update activity template."""
    service = ActivityService(db)
    template = await service.update_activity_template(template_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Activity template not found")
    return template


@router.delete("/templates/{template_id}")
async def delete_activity_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete activity template."""
    service = ActivityService(db)
    success = await service.delete_activity_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity template not found")
    return {"message": "Activity template deleted successfully"}


# Activity Endpoints
@router.post("/", response_model=ActivityResponse)
async def create_activity(
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new activity."""
    service = ActivityService(db)
    return await service.create_activity(activity_data)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get activity by ID."""
    service = ActivityService(db)
    activity = await service.get_activity(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.get("/", response_model=List[ActivityResponse])
async def get_activities(
    activity_type: Optional[str] = Query(None),
    template_id: Optional[UUID] = Query(None),
    created_by: Optional[UUID] = Query(None),
    is_mandatory: Optional[bool] = Query(None),
    is_graded: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get activities with optional filters."""
    service = ActivityService(db)
    return await service.get_activities(
        activity_type=activity_type,
        template_id=template_id,
        created_by=created_by,
        is_mandatory=is_mandatory,
        is_graded=is_graded,
        search=search,
        skip=skip,
        limit=limit
    )


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: UUID,
    activity_data: ActivityUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update activity."""
    service = ActivityService(db)
    activity = await service.update_activity(activity_id, activity_data)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete activity."""
    service = ActivityService(db)
    success = await service.delete_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Activity not found")
    return {"message": "Activity deleted successfully"}


# Course Activity Endpoints
@router.post("/course-activities", response_model=CourseActivityResponse)
async def create_course_activity(
    course_activity_data: CourseActivityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new course activity."""
    service = ActivityService(db)
    return await service.create_course_activity(course_activity_data)


@router.get("/course-activities/{course_activity_id}", response_model=CourseActivityResponse)
async def get_course_activity(
    course_activity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get course activity by ID."""
    service = ActivityService(db)
    course_activity = await service.get_course_activity(course_activity_id)
    if not course_activity:
        raise HTTPException(status_code=404, detail="Course activity not found")
    return course_activity


@router.get("/courses/{course_id}/activities", response_model=List[CourseActivityResponse])
async def get_course_activities(
    course_id: UUID,
    module_id: Optional[UUID] = Query(None),
    is_required: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get activities for a course ordered by sequence."""
    service = ActivityService(db)
    return await service.get_course_activities(
        course_id=course_id,
        module_id=module_id,
        is_required=is_required,
        skip=skip,
        limit=limit
    )


@router.put("/course-activities/{course_activity_id}", response_model=CourseActivityResponse)
async def update_course_activity(
    course_activity_id: UUID,
    course_activity_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Update course activity."""
    service = ActivityService(db)
    course_activity = await service.update_course_activity(course_activity_id, course_activity_data)
    if not course_activity:
        raise HTTPException(status_code=404, detail="Course activity not found")
    return course_activity


@router.delete("/course-activities/{course_activity_id}")
async def delete_course_activity(
    course_activity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete course activity."""
    service = ActivityService(db)
    success = await service.delete_course_activity(course_activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course activity not found")
    return {"message": "Course activity deleted successfully"}


@router.post("/courses/{course_id}/reorder-activities")
async def reorder_course_activities(
    course_id: UUID,
    activity_order: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db)
):
    """Reorder activities in a course."""
    service = ActivityService(db)
    success = await service.reorder_course_activities(course_id, activity_order)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reorder activities")
    return {"message": "Activities reordered successfully"}


@router.get("/templates/{template_id}/analytics")
async def get_template_analytics(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for an activity template."""
    service = ActivityService(db)
    return await service.get_template_analytics(template_id)


@router.get("/courses/{course_id}/activity-summary")
async def get_course_activity_summary(
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get activity summary for a course."""
    service = ActivityService(db)
    return await service.get_course_activity_summary(course_id)