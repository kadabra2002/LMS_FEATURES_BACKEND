from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.schedule import CourseSchedule, UserCourseEnrollment
from app.schemas.schedule import (
    CourseScheduleCreate, CourseScheduleUpdate,
    UserCourseEnrollmentCreate, UserCourseEnrollmentUpdate
)


class ScheduleService:
    """Service for managing course schedules and enrollments."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Course Schedule Methods
    async def create_course_schedule(self, schedule_data: CourseScheduleCreate) -> CourseSchedule:
        """Create a new course schedule."""
        schedule = CourseSchedule(**schedule_data.model_dump())
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def get_course_schedule(self, schedule_id: UUID) -> Optional[CourseSchedule]:
        """Get course schedule by ID with related enrollments."""
        result = await self.db.execute(
            select(CourseSchedule)
            .options(selectinload(CourseSchedule.enrollments))
            .where(CourseSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_course_schedules(
        self,
        course_id: Optional[UUID] = None,
        schedule_type: Optional[str] = None,
        delivery_mode: Optional[str] = None,
        status: Optional[str] = None,
        is_mandatory: Optional[bool] = None,
        created_by: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseSchedule]:
        """Get course schedules with optional filters."""
        query = select(CourseSchedule)
        
        if course_id:
            query = query.where(CourseSchedule.course_id == course_id)
        if schedule_type:
            query = query.where(CourseSchedule.schedule_type == schedule_type)
        if delivery_mode:
            query = query.where(CourseSchedule.delivery_mode == delivery_mode)
        if status:
            query = query.where(CourseSchedule.status == status)
        if is_mandatory is not None:
            query = query.where(CourseSchedule.is_mandatory == is_mandatory)
        if created_by:
            query = query.where(CourseSchedule.created_by == created_by)
        
        query = query.offset(skip).limit(limit).order_by(CourseSchedule.start_date.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_course_schedule(
        self,
        schedule_id: UUID,
        schedule_data: CourseScheduleUpdate
    ) -> Optional[CourseSchedule]:
        """Update course schedule."""
        existing = await self.get_course_schedule(schedule_id)
        if not existing:
            return None
        
        update_data = schedule_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(CourseSchedule)
            .where(CourseSchedule.id == schedule_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_course_schedule(schedule_id)
    
    async def delete_course_schedule(self, schedule_id: UUID) -> bool:
        """Delete course schedule and related enrollments."""
        result = await self.db.execute(
            delete(CourseSchedule).where(CourseSchedule.id == schedule_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # User Course Enrollment Methods
    async def create_enrollment(self, enrollment_data: UserCourseEnrollmentCreate) -> UserCourseEnrollment:
        """Create a new course enrollment."""
        # Check if schedule has available slots
        schedule = await self.get_course_schedule(enrollment_data.schedule_id)
        if schedule and schedule.max_enrollments:
            if schedule.current_enrollments >= schedule.max_enrollments:
                raise ValueError("Course schedule is full")
        
        enrollment = UserCourseEnrollment(**enrollment_data.model_dump())
        self.db.add(enrollment)
        
        # Update enrollment count
        if schedule:
            await self.db.execute(
                update(CourseSchedule)
                .where(CourseSchedule.id == enrollment_data.schedule_id)
                .values(current_enrollments=CourseSchedule.current_enrollments + 1)
            )
        
        await self.db.commit()
        await self.db.refresh(enrollment)
        return enrollment
    
    async def get_enrollment(self, enrollment_id: UUID) -> Optional[UserCourseEnrollment]:
        """Get enrollment by ID."""
        result = await self.db.execute(
            select(UserCourseEnrollment).where(UserCourseEnrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_enrollments(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        course_id: Optional[UUID] = None,
        enrollment_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserCourseEnrollment]:
        """Get user's course enrollments."""
        query = select(UserCourseEnrollment).where(UserCourseEnrollment.user_id == user_id)
        
        if status:
            query = query.where(UserCourseEnrollment.status == status)
        if course_id:
            query = query.where(UserCourseEnrollment.course_id == course_id)
        if enrollment_type:
            query = query.where(UserCourseEnrollment.enrollment_type == enrollment_type)
        
        query = query.offset(skip).limit(limit).order_by(UserCourseEnrollment.enrollment_date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_schedule_enrollments(
        self,
        schedule_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserCourseEnrollment]:
        """Get enrollments for a specific schedule."""
        query = select(UserCourseEnrollment).where(UserCourseEnrollment.schedule_id == schedule_id)
        
        if status:
            query = query.where(UserCourseEnrollment.status == status)
        
        query = query.offset(skip).limit(limit).order_by(UserCourseEnrollment.enrollment_date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_enrollment(
        self,
        enrollment_id: UUID,
        enrollment_data: UserCourseEnrollmentUpdate
    ) -> Optional[UserCourseEnrollment]:
        """Update course enrollment."""
        existing = await self.get_enrollment(enrollment_id)
        if not existing:
            return None
        
        update_data = enrollment_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(UserCourseEnrollment)
            .where(UserCourseEnrollment.id == enrollment_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_enrollment(enrollment_id)
    
    async def cancel_enrollment(self, enrollment_id: UUID) -> bool:
        """Cancel a course enrollment and update schedule count."""
        enrollment = await self.get_enrollment(enrollment_id)
        if not enrollment:
            return False
        
        # Update enrollment status
        await self.db.execute(
            update(UserCourseEnrollment)
            .where(UserCourseEnrollment.id == enrollment_id)
            .values(status="cancelled")
        )
        
        # Update schedule enrollment count
        await self.db.execute(
            update(CourseSchedule)
            .where(CourseSchedule.id == enrollment.schedule_id)
            .values(current_enrollments=CourseSchedule.current_enrollments - 1)
        )
        
        await self.db.commit()
        return True
    
    # Schedule Analytics
    async def get_schedule_analytics(self, schedule_id: UUID) -> Dict[str, Any]:
        """Get comprehensive analytics for a course schedule."""
        schedule = await self.get_course_schedule(schedule_id)
        if not schedule:
            return {"error": "Schedule not found"}
        
        # Get all enrollments for this schedule
        enrollments = await self.get_schedule_enrollments(schedule_id, limit=1000)
        
        total_enrollments = len(enrollments)
        active_enrollments = len([e for e in enrollments if e.status == "active"])
        completed_enrollments = len([e for e in enrollments if e.status == "completed"])
        dropped_enrollments = len([e for e in enrollments if e.status == "dropped"])
        
        # Calculate completion rate
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Calculate average progress
        progress_scores = [e.progress_percentage for e in enrollments if e.progress_percentage is not None]
        average_progress = sum(progress_scores) / len(progress_scores) if progress_scores else 0
        
        # Enrollment type breakdown
        enrollment_types = {}
        for enrollment in enrollments:
            enrollment_type = enrollment.enrollment_type
            enrollment_types[enrollment_type] = enrollment_types.get(enrollment_type, 0) + 1
        
        return {
            "schedule_id": str(schedule_id),
            "schedule_name": schedule.schedule_name,
            "enrollment_stats": {
                "total_enrollments": total_enrollments,
                "active_enrollments": active_enrollments,
                "completed_enrollments": completed_enrollments,
                "dropped_enrollments": dropped_enrollments,
                "completion_rate": round(completion_rate, 2),
                "capacity_utilization": (total_enrollments / schedule.max_enrollments * 100) if schedule.max_enrollments else None
            },
            "performance": {
                "average_progress_percentage": round(average_progress, 2),
                "average_grade": self._calculate_average_grade(enrollments)
            },
            "enrollment_breakdown": enrollment_types
        }
    
    def _calculate_average_grade(self, enrollments: List[UserCourseEnrollment]) -> Optional[float]:
        """Calculate average numerical grade from enrollments."""
        scores = [e.score for e in enrollments if e.score is not None]
        return round(sum(scores) / len(scores), 2) if scores else None
    
    async def get_available_schedules(
        self,
        course_id: UUID,
        user_id: Optional[UUID] = None
    ) -> List[CourseSchedule]:
        """Get available schedules for a course that a user can enroll in."""
        current_time = datetime.utcnow()
        
        query = select(CourseSchedule).where(
            and_(
                CourseSchedule.course_id == course_id,
                CourseSchedule.status == "published",
                or_(
                    CourseSchedule.registration_end.is_(None),
                    CourseSchedule.registration_end > current_time
                ),
                or_(
                    CourseSchedule.registration_start.is_(None),
                    CourseSchedule.registration_start <= current_time
                )
            )
        )
        
        result = await self.db.execute(query)
        schedules = result.scalars().all()
        
        # Filter out full schedules
        available_schedules = []
        for schedule in schedules:
            if schedule.max_enrollments is None or schedule.current_enrollments < schedule.max_enrollments:
                # Check if user is already enrolled (if user_id provided)
                if user_id:
                    existing_enrollment = await self.db.execute(
                        select(UserCourseEnrollment).where(
                            and_(
                                UserCourseEnrollment.user_id == user_id,
                                UserCourseEnrollment.schedule_id == schedule.id,
                                UserCourseEnrollment.status.in_(["enrolled", "active"])
                            )
                        )
                    )
                    if not existing_enrollment.scalar_one_or_none():
                        available_schedules.append(schedule)
                else:
                    available_schedules.append(schedule)
        
        return available_schedules