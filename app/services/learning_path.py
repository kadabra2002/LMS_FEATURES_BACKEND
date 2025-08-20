from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.learning_path import LearningPath, LearningPathCourse, UserLearningPath
from app.schemas.learning_path import (
    LearningPathCreate, LearningPathUpdate,
    LearningPathCourseCreate, UserLearningPathCreate, UserLearningPathUpdate
)


class LearningPathService:
    """Service for managing adaptive learning paths and personalized learning journeys."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Learning Path Methods
    async def create_learning_path(self, path_data: LearningPathCreate) -> LearningPath:
        """Create a new learning path."""
        path = LearningPath(**path_data.model_dump())
        self.db.add(path)
        await self.db.commit()
        await self.db.refresh(path)
        return path
    
    async def get_learning_path(self, path_id: UUID) -> Optional[LearningPath]:
        """Get learning path by ID with related courses."""
        result = await self.db.execute(
            select(LearningPath)
            .options(selectinload(LearningPath.path_courses))
            .where(LearningPath.id == path_id)
        )
        return result.scalar_one_or_none()
    
    async def get_learning_paths(
        self,
        skill_level: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_mandatory: Optional[bool] = None,
        created_by: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LearningPath]:
        """Get learning paths with optional filters."""
        query = select(LearningPath)
        
        if skill_level:
            query = query.where(LearningPath.skill_level == skill_level)
        if is_active is not None:
            query = query.where(LearningPath.is_active == is_active)
        if is_mandatory is not None:
            query = query.where(LearningPath.is_mandatory == is_mandatory)
        if created_by:
            query = query.where(LearningPath.created_by == created_by)
        if search:
            query = query.where(
                or_(
                    LearningPath.name.ilike(f"%{search}%"),
                    LearningPath.description.ilike(f"%{search}%")
                )
            )
        
        query = query.offset(skip).limit(limit).order_by(LearningPath.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_learning_path(
        self,
        path_id: UUID,
        path_data: LearningPathUpdate
    ) -> Optional[LearningPath]:
        """Update learning path."""
        existing = await self.get_learning_path(path_id)
        if not existing:
            return None
        
        update_data = path_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(LearningPath)
            .where(LearningPath.id == path_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_learning_path(path_id)
    
    async def delete_learning_path(self, path_id: UUID) -> bool:
        """Delete learning path and related records."""
        result = await self.db.execute(
            delete(LearningPath).where(LearningPath.id == path_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Learning Path Course Methods
    async def add_course_to_path(self, course_data: LearningPathCourseCreate) -> LearningPathCourse:
        """Add a course to a learning path."""
        path_course = LearningPathCourse(**course_data.model_dump())
        self.db.add(path_course)
        await self.db.commit()
        await self.db.refresh(path_course)
        return path_course
    
    async def get_path_courses(self, path_id: UUID) -> List[LearningPathCourse]:
        """Get courses in a learning path ordered by sequence."""
        result = await self.db.execute(
            select(LearningPathCourse)
            .where(LearningPathCourse.path_id == path_id)
            .order_by(LearningPathCourse.order_sequence)
        )
        return result.scalars().all()
    
    async def update_path_course(
        self,
        path_id: UUID,
        course_id: UUID,
        course_data: Dict[str, Any]
    ) -> Optional[LearningPathCourse]:
        """Update course configuration in a learning path."""
        result = await self.db.execute(
            select(LearningPathCourse)
            .where(
                and_(
                    LearningPathCourse.path_id == path_id,
                    LearningPathCourse.course_id == course_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        if not existing:
            return None
        
        await self.db.execute(
            update(LearningPathCourse)
            .where(
                and_(
                    LearningPathCourse.path_id == path_id,
                    LearningPathCourse.course_id == course_id
                )
            )
            .values(**course_data)
        )
        await self.db.commit()
        
        # Return updated record
        result = await self.db.execute(
            select(LearningPathCourse)
            .where(
                and_(
                    LearningPathCourse.path_id == path_id,
                    LearningPathCourse.course_id == course_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def remove_course_from_path(self, path_id: UUID, course_id: UUID) -> bool:
        """Remove a course from a learning path."""
        result = await self.db.execute(
            delete(LearningPathCourse)
            .where(
                and_(
                    LearningPathCourse.path_id == path_id,
                    LearningPathCourse.course_id == course_id
                )
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # User Learning Path Methods
    async def enroll_user_in_path(self, enrollment_data: UserLearningPathCreate) -> UserLearningPath:
        """Enroll a user in a learning path."""
        # Get the learning path to set total steps
        path_courses = await self.get_path_courses(enrollment_data.path_id)
        
        enrollment = UserLearningPath(**enrollment_data.model_dump())
        enrollment.total_steps = len(path_courses)
        
        # Set current course to the first course if available
        if path_courses:
            enrollment.current_course_id = path_courses[0].course_id
        
        self.db.add(enrollment)
        await self.db.commit()
        await self.db.refresh(enrollment)
        return enrollment
    
    async def get_user_path_enrollment(self, enrollment_id: UUID) -> Optional[UserLearningPath]:
        """Get user learning path enrollment by ID."""
        result = await self.db.execute(
            select(UserLearningPath).where(UserLearningPath.id == enrollment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_path_enrollments(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserLearningPath]:
        """Get user's learning path enrollments."""
        query = select(UserLearningPath).where(UserLearningPath.user_id == user_id)
        
        if status:
            query = query.where(UserLearningPath.status == status)
        
        query = query.offset(skip).limit(limit).order_by(UserLearningPath.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_user_path_enrollment(
        self,
        enrollment_id: UUID,
        enrollment_data: UserLearningPathUpdate
    ) -> Optional[UserLearningPath]:
        """Update user learning path enrollment."""
        existing = await self.get_user_path_enrollment(enrollment_id)
        if not existing:
            return None
        
        update_data = enrollment_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(UserLearningPath)
            .where(UserLearningPath.id == enrollment_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_user_path_enrollment(enrollment_id)
    
    # Adaptive Learning Methods
    async def get_personalized_recommendations(
        self,
        user_id: UUID,
        path_id: UUID
    ) -> Dict[str, Any]:
        """Get personalized course recommendations based on user's learning data."""
        # Get user's enrollment in the path
        result = await self.db.execute(
            select(UserLearningPath)
            .where(
                and_(
                    UserLearningPath.user_id == user_id,
                    UserLearningPath.path_id == path_id
                )
            )
        )
        enrollment = result.scalar_one_or_none()
        
        if not enrollment:
            return {"error": "User not enrolled in this path"}
        
        # Get path courses
        path_courses = await self.get_path_courses(path_id)
        
        # Simple recommendation logic (can be enhanced with ML algorithms)
        recommendations = []
        
        for course in path_courses:
            if course.order_sequence > enrollment.current_step:
                # Check prerequisites
                prerequisites_met = True  # Simplified - would check actual progress
                
                if prerequisites_met:
                    recommendation_score = self._calculate_recommendation_score(
                        course, enrollment.personalization_data
                    )
                    
                    recommendations.append({
                        "course_id": str(course.course_id),
                        "order_sequence": course.order_sequence,
                        "recommendation_score": recommendation_score,
                        "is_mandatory": course.is_mandatory,
                        "estimated_duration_hours": course.estimated_duration_hours,
                        "points_awarded": course.points_awarded,
                        "reasons": self._get_recommendation_reasons(course, enrollment)
                    })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return {
            "user_id": str(user_id),
            "path_id": str(path_id),
            "current_step": enrollment.current_step,
            "total_steps": enrollment.total_steps,
            "recommendations": recommendations[:5]  # Top 5 recommendations
        }
    
    async def get_next_course(self, user_id: UUID, path_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the next course for a user in their learning path."""
        # Get user's enrollment
        result = await self.db.execute(
            select(UserLearningPath)
            .where(
                and_(
                    UserLearningPath.user_id == user_id,
                    UserLearningPath.path_id == path_id
                )
            )
        )
        enrollment = result.scalar_one_or_none()
        
        if not enrollment:
            return None
        
        # Get the next course in sequence
        result = await self.db.execute(
            select(LearningPathCourse)
            .where(
                and_(
                    LearningPathCourse.path_id == path_id,
                    LearningPathCourse.order_sequence > enrollment.current_step
                )
            )
            .order_by(LearningPathCourse.order_sequence)
            .limit(1)
        )
        next_course = result.scalar_one_or_none()
        
        if not next_course:
            return None
        
        return {
            "course_id": str(next_course.course_id),
            "order_sequence": next_course.order_sequence,
            "is_mandatory": next_course.is_mandatory,
            "estimated_duration_hours": next_course.estimated_duration_hours,
            "points_awarded": next_course.points_awarded,
            "prerequisites": next_course.prerequisites,
            "unlock_criteria": next_course.unlock_criteria
        }
    
    def _calculate_recommendation_score(
        self,
        course: LearningPathCourse,
        personalization_data: Dict[str, Any]
    ) -> float:
        """Calculate recommendation score for a course based on personalization data."""
        base_score = 50.0  # Base score
        
        # Adjust based on course properties
        if course.is_mandatory:
            base_score += 30.0
        
        # Adjust based on user preferences (simplified)
        if personalization_data:
            preferred_difficulty = personalization_data.get("preferred_difficulty", "medium")
            if preferred_difficulty == "easy" and course.weight < 0.8:
                base_score += 10.0
            elif preferred_difficulty == "hard" and course.weight > 1.2:
                base_score += 10.0
        
        return min(base_score, 100.0)
    
    def _get_recommendation_reasons(
        self,
        course: LearningPathCourse,
        enrollment: UserLearningPath
    ) -> List[str]:
        """Get reasons why a course is recommended."""
        reasons = []
        
        if course.is_mandatory:
            reasons.append("Required course in your learning path")
        
        if course.order_sequence == enrollment.current_step + 1:
            reasons.append("Next course in sequence")
        
        if course.points_awarded > 0:
            reasons.append(f"Earn {course.points_awarded} points upon completion")
        
        if course.estimated_duration_hours and course.estimated_duration_hours <= 2:
            reasons.append("Quick course that can be completed in 2 hours or less")
        
        return reasons
    
    async def get_path_analytics(self, path_id: UUID) -> Dict[str, Any]:
        """Get analytics for a learning path."""
        # Get enrollment statistics
        result = await self.db.execute(
            select(UserLearningPath).where(UserLearningPath.path_id == path_id)
        )
        enrollments = result.scalars().all()
        
        total_enrollments = len(enrollments)
        completed_enrollments = len([e for e in enrollments if e.status == "completed"])
        active_enrollments = len([e for e in enrollments if e.status == "active"])
        
        # Calculate completion rate
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Calculate average progress
        average_progress = sum(e.progress_percentage for e in enrollments) / total_enrollments if total_enrollments > 0 else 0
        
        # Get course analytics
        path_courses = await self.get_path_courses(path_id)
        
        return {
            "path_id": str(path_id),
            "enrollment_stats": {
                "total_enrollments": total_enrollments,
                "completed_enrollments": completed_enrollments,
                "active_enrollments": active_enrollments,
                "dropped_enrollments": len([e for e in enrollments if e.status == "dropped"]),
                "completion_rate": round(completion_rate, 2)
            },
            "progress_stats": {
                "average_progress_percentage": round(average_progress, 2),
                "average_points_earned": round(sum(e.points_earned for e in enrollments) / total_enrollments, 2) if total_enrollments > 0 else 0
            },
            "path_structure": {
                "total_courses": len(path_courses),
                "mandatory_courses": len([c for c in path_courses if c.is_mandatory]),
                "optional_courses": len([c for c in path_courses if not c.is_mandatory]),
                "total_points_available": sum(c.points_awarded for c in path_courses)
            }
        }