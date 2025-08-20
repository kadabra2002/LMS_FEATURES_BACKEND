from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.learning_path import (
    LearningPathCreate, LearningPathUpdate, LearningPathResponse,
    LearningPathCourseCreate, LearningPathCourseResponse,
    UserLearningPathCreate, UserLearningPathUpdate, UserLearningPathResponse
)
from app.services.learning_path import LearningPathService

router = APIRouter()


# Learning Path Endpoints
@router.post("/", response_model=LearningPathResponse)
async def create_learning_path(
    path_data: LearningPathCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new learning path."""
    service = LearningPathService(db)
    return await service.create_learning_path(path_data)


@router.get("/{path_id}", response_model=LearningPathResponse)
async def get_learning_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get learning path by ID."""
    service = LearningPathService(db)
    path = await service.get_learning_path(path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return path


@router.get("/", response_model=List[LearningPathResponse])
async def get_learning_paths(
    skill_level: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_mandatory: Optional[bool] = Query(None),
    created_by: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get learning paths with optional filters."""
    service = LearningPathService(db)
    return await service.get_learning_paths(
        skill_level=skill_level,
        is_active=is_active,
        is_mandatory=is_mandatory,
        created_by=created_by,
        search=search,
        skip=skip,
        limit=limit
    )


@router.put("/{path_id}", response_model=LearningPathResponse)
async def update_learning_path(
    path_id: UUID,
    path_data: LearningPathUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update learning path."""
    service = LearningPathService(db)
    path = await service.update_learning_path(path_id, path_data)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return path


@router.delete("/{path_id}")
async def delete_learning_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete learning path."""
    service = LearningPathService(db)
    success = await service.delete_learning_path(path_id)
    if not success:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return {"message": "Learning path deleted successfully"}


# Learning Path Course Endpoints
@router.post("/{path_id}/courses", response_model=LearningPathCourseResponse)
async def add_course_to_path(
    path_id: UUID,
    course_data: LearningPathCourseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a course to a learning path."""
    if course_data.path_id != path_id:
        raise HTTPException(status_code=400, detail="Path ID mismatch")
    
    service = LearningPathService(db)
    return await service.add_course_to_path(course_data)


@router.get("/{path_id}/courses", response_model=List[LearningPathCourseResponse])
async def get_path_courses(
    path_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get courses in a learning path."""
    service = LearningPathService(db)
    return await service.get_path_courses(path_id)


@router.put("/{path_id}/courses/{course_id}", response_model=LearningPathCourseResponse)
async def update_path_course(
    path_id: UUID,
    course_id: UUID,
    course_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update course configuration in a learning path."""
    service = LearningPathService(db)
    path_course = await service.update_path_course(path_id, course_id, course_data)
    if not path_course:
        raise HTTPException(status_code=404, detail="Course not found in path")
    return path_course


@router.delete("/{path_id}/courses/{course_id}")
async def remove_course_from_path(
    path_id: UUID,
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Remove a course from a learning path."""
    service = LearningPathService(db)
    success = await service.remove_course_from_path(path_id, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found in path")
    return {"message": "Course removed from path successfully"}


# User Learning Path Endpoints
@router.post("/enrollments", response_model=UserLearningPathResponse)
async def enroll_user_in_path(
    enrollment_data: UserLearningPathCreate,
    db: AsyncSession = Depends(get_db)
):
    """Enroll a user in a learning path."""
    service = LearningPathService(db)
    return await service.enroll_user_in_path(enrollment_data)


@router.get("/enrollments/{enrollment_id}", response_model=UserLearningPathResponse)
async def get_user_path_enrollment(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user learning path enrollment by ID."""
    service = LearningPathService(db)
    enrollment = await service.get_user_path_enrollment(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.get("/users/{user_id}/enrollments", response_model=List[UserLearningPathResponse])
async def get_user_path_enrollments(
    user_id: UUID,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get user's learning path enrollments."""
    service = LearningPathService(db)
    return await service.get_user_path_enrollments(
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.put("/enrollments/{enrollment_id}", response_model=UserLearningPathResponse)
async def update_user_path_enrollment(
    enrollment_id: UUID,
    enrollment_data: UserLearningPathUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user learning path enrollment."""
    service = LearningPathService(db)
    enrollment = await service.update_user_path_enrollment(enrollment_id, enrollment_data)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.post("/{path_id}/users/{user_id}/recommendations")
async def get_personalized_recommendations(
    path_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get personalized course recommendations for a user in a learning path."""
    service = LearningPathService(db)
    return await service.get_personalized_recommendations(user_id, path_id)


@router.post("/{path_id}/users/{user_id}/next-course")
async def get_next_course(
    path_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get the next course for a user in their learning path."""
    service = LearningPathService(db)
    next_course = await service.get_next_course(user_id, path_id)
    if not next_course:
        raise HTTPException(status_code=404, detail="No next course available")
    return next_course


@router.get("/{path_id}/analytics")
async def get_path_analytics(
    path_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a learning path."""
    service = LearningPathService(db)
    return await service.get_path_analytics(path_id)