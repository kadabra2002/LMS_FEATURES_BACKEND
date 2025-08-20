from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.progress import ProgressTracking, UserAssessment, Attendance
from app.schemas.progress import (
    ProgressTrackingCreate, ProgressTrackingUpdate,
    UserAssessmentCreate, UserAssessmentUpdate,
    AttendanceCreate, AttendanceUpdate
)


class ProgressService:
    """Service for managing learning progress tracking, assessments, and attendance."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Progress Tracking Methods
    async def create_progress_tracking(self, progress_data: ProgressTrackingCreate) -> ProgressTracking:
        """Create a new progress tracking record."""
        progress = ProgressTracking(**progress_data.model_dump())
        self.db.add(progress)
        await self.db.commit()
        await self.db.refresh(progress)
        return progress
    
    async def get_progress_tracking(self, progress_id: UUID) -> Optional[ProgressTracking]:
        """Get progress tracking by ID."""
        result = await self.db.execute(
            select(ProgressTracking)
            .options(
                selectinload(ProgressTracking.assessments),
                selectinload(ProgressTracking.attendance_records)
            )
            .where(ProgressTracking.id == progress_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_progress(
        self,
        user_id: UUID,
        course_id: Optional[UUID] = None,
        module_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProgressTracking]:
        """Get user's progress tracking records with optional filters."""
        query = select(ProgressTracking).where(ProgressTracking.user_id == user_id)
        
        if course_id:
            query = query.where(ProgressTracking.course_id == course_id)
        if module_id:
            query = query.where(ProgressTracking.module_id == module_id)
        if status:
            query = query.where(ProgressTracking.completion_status == status)
        
        query = query.offset(skip).limit(limit).order_by(ProgressTracking.updated_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_course_progress(
        self,
        course_id: UUID,
        user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProgressTracking]:
        """Get progress tracking records for a course."""
        query = select(ProgressTracking).where(ProgressTracking.course_id == course_id)
        
        if user_id:
            query = query.where(ProgressTracking.user_id == user_id)
        if status:
            query = query.where(ProgressTracking.completion_status == status)
        
        query = query.offset(skip).limit(limit).order_by(ProgressTracking.updated_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_progress_tracking(
        self, 
        progress_id: UUID, 
        progress_data: ProgressTrackingUpdate
    ) -> Optional[ProgressTracking]:
        """Update progress tracking record."""
        # Get existing record
        existing = await self.get_progress_tracking(progress_id)
        if not existing:
            return None
        
        # Update fields
        update_data = progress_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(ProgressTracking)
            .where(ProgressTracking.id == progress_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_progress_tracking(progress_id)
    
    async def delete_progress_tracking(self, progress_id: UUID) -> bool:
        """Delete progress tracking record."""
        result = await self.db.execute(
            delete(ProgressTracking).where(ProgressTracking.id == progress_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # User Assessment Methods
    async def create_user_assessment(self, assessment_data: UserAssessmentCreate) -> UserAssessment:
        """Create a new user assessment record."""
        assessment = UserAssessment(**assessment_data.model_dump())
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment
    
    async def get_user_assessment(self, assessment_id: UUID) -> Optional[UserAssessment]:
        """Get user assessment by ID."""
        result = await self.db.execute(
            select(UserAssessment)
            .options(selectinload(UserAssessment.user_answers))
            .where(UserAssessment.id == assessment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_assessments(
        self,
        user_id: UUID,
        assessment_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserAssessment]:
        """Get user's assessment records."""
        query = select(UserAssessment).where(UserAssessment.user_id == user_id)
        
        if assessment_id:
            query = query.where(UserAssessment.assessment_id == assessment_id)
        if status:
            query = query.where(UserAssessment.status == status)
        
        query = query.offset(skip).limit(limit).order_by(UserAssessment.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_user_assessment(
        self,
        assessment_id: UUID,
        assessment_data: UserAssessmentUpdate
    ) -> Optional[UserAssessment]:
        """Update user assessment record."""
        existing = await self.get_user_assessment(assessment_id)
        if not existing:
            return None
        
        update_data = assessment_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(UserAssessment)
            .where(UserAssessment.id == assessment_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_user_assessment(assessment_id)
    
    # Attendance Methods
    async def create_attendance(self, attendance_data: AttendanceCreate) -> Attendance:
        """Create a new attendance record."""
        attendance = Attendance(**attendance_data.model_dump())
        self.db.add(attendance)
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance
    
    async def get_attendance(self, attendance_id: UUID) -> Optional[Attendance]:
        """Get attendance by ID."""
        result = await self.db.execute(
            select(Attendance).where(Attendance.id == attendance_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_attendance(
        self,
        user_id: UUID,
        course_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Attendance]:
        """Get user's attendance records."""
        query = select(Attendance).where(Attendance.user_id == user_id)
        
        if course_id:
            query = query.where(Attendance.course_id == course_id)
        if session_id:
            query = query.where(Attendance.session_id == session_id)
        if status:
            query = query.where(Attendance.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Attendance.attended_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_attendance(
        self,
        attendance_id: UUID,
        attendance_data: AttendanceUpdate
    ) -> Optional[Attendance]:
        """Update attendance record."""
        existing = await self.get_attendance(attendance_id)
        if not existing:
            return None
        
        update_data = attendance_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Attendance)
            .where(Attendance.id == attendance_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_attendance(attendance_id)
    
    # Analytics Methods
    async def get_user_progress_summary(
        self, 
        user_id: UUID, 
        course_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get comprehensive progress summary for a user."""
        # Base query for progress tracking
        progress_query = select(ProgressTracking).where(ProgressTracking.user_id == user_id)
        if course_id:
            progress_query = progress_query.where(ProgressTracking.course_id == course_id)
        
        progress_result = await self.db.execute(progress_query)
        progress_records = progress_result.scalars().all()
        
        # Calculate summary statistics
        total_courses = len(set(p.course_id for p in progress_records))
        completed_courses = len([p for p in progress_records if p.completion_status == "completed"])
        in_progress_courses = len([p for p in progress_records if p.completion_status == "in_progress"])
        
        total_time = sum(p.time_spent_minutes for p in progress_records)
        average_score = sum(p.overall_score for p in progress_records if p.overall_score) / len(progress_records) if progress_records else 0
        
        # Get assessment summary
        assessment_query = select(UserAssessment).where(UserAssessment.user_id == user_id)
        assessment_result = await self.db.execute(assessment_query)
        assessments = assessment_result.scalars().all()
        
        passed_assessments = len([a for a in assessments if a.status == "completed" and a.percentage and a.percentage >= 70])
        total_assessments = len([a for a in assessments if a.status == "completed"])
        
        return {
            "user_id": str(user_id),
            "course_id": str(course_id) if course_id else None,
            "overview": {
                "total_courses": total_courses,
                "completed_courses": completed_courses,
                "in_progress_courses": in_progress_courses,
                "completion_rate": (completed_courses / total_courses * 100) if total_courses > 0 else 0
            },
            "time_analytics": {
                "total_time_minutes": total_time,
                "total_time_hours": round(total_time / 60, 2),
                "average_time_per_course": round(total_time / total_courses, 2) if total_courses > 0 else 0
            },
            "performance": {
                "average_score": round(average_score, 2),
                "passed_assessments": passed_assessments,
                "total_assessments": total_assessments,
                "pass_rate": (passed_assessments / total_assessments * 100) if total_assessments > 0 else 0
            }
        }
    
    async def get_course_progress_summary(self, course_id: UUID) -> Dict[str, Any]:
        """Get comprehensive progress summary for a course."""
        # Get all progress records for the course
        progress_query = select(ProgressTracking).where(ProgressTracking.course_id == course_id)
        progress_result = await self.db.execute(progress_query)
        progress_records = progress_result.scalars().all()
        
        total_enrollments = len(progress_records)
        completed_enrollments = len([p for p in progress_records if p.completion_status == "completed"])
        in_progress_enrollments = len([p for p in progress_records if p.completion_status == "in_progress"])
        
        average_completion_percentage = sum(p.completion_percentage for p in progress_records) / total_enrollments if total_enrollments > 0 else 0
        average_time = sum(p.time_spent_minutes for p in progress_records) / total_enrollments if total_enrollments > 0 else 0
        
        return {
            "course_id": str(course_id),
            "enrollment_stats": {
                "total_enrollments": total_enrollments,
                "completed_enrollments": completed_enrollments,
                "in_progress_enrollments": in_progress_enrollments,
                "completion_rate": (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
            },
            "engagement": {
                "average_completion_percentage": round(average_completion_percentage, 2),
                "average_time_minutes": round(average_time, 2),
                "average_time_hours": round(average_time / 60, 2)
            }
        }