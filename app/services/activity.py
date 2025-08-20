from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.activity import ActivityTemplate, Activity, CourseActivity
from app.schemas.activity import (
    ActivityTemplateCreate, ActivityTemplateUpdate,
    ActivityCreate, ActivityUpdate,
    CourseActivityCreate
)


class ActivityService:
    """Service for managing activity templates, activities, and course activities."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Activity Template Methods
    async def create_activity_template(self, template_data: ActivityTemplateCreate) -> ActivityTemplate:
        """Create a new activity template."""
        template = ActivityTemplate(**template_data.model_dump())
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template
    
    async def get_activity_template(self, template_id: UUID) -> Optional[ActivityTemplate]:
        """Get activity template by ID."""
        result = await self.db.execute(
            select(ActivityTemplate)
            .options(selectinload(ActivityTemplate.activities))
            .where(ActivityTemplate.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def get_activity_templates(
        self,
        activity_type: Optional[str] = None,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
        is_reusable: Optional[bool] = None,
        created_by: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ActivityTemplate]:
        """Get activity templates with optional filters."""
        query = select(ActivityTemplate)
        
        if activity_type:
            query = query.where(ActivityTemplate.activity_type == activity_type)
        if category:
            query = query.where(ActivityTemplate.category == category)
        if is_public is not None:
            query = query.where(ActivityTemplate.is_public == is_public)
        if is_reusable is not None:
            query = query.where(ActivityTemplate.is_reusable == is_reusable)
        if created_by:
            query = query.where(ActivityTemplate.created_by == created_by)
        if search:
            query = query.where(
                or_(
                    ActivityTemplate.name.ilike(f"%{search}%"),
                    ActivityTemplate.description.ilike(f"%{search}%")
                )
            )
        
        query = query.offset(skip).limit(limit).order_by(ActivityTemplate.usage_count.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_activity_template(
        self,
        template_id: UUID,
        template_data: ActivityTemplateUpdate
    ) -> Optional[ActivityTemplate]:
        """Update activity template."""
        existing = await self.get_activity_template(template_id)
        if not existing:
            return None
        
        update_data = template_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(ActivityTemplate)
            .where(ActivityTemplate.id == template_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_activity_template(template_id)
    
    async def delete_activity_template(self, template_id: UUID) -> bool:
        """Delete activity template."""
        result = await self.db.execute(
            delete(ActivityTemplate).where(ActivityTemplate.id == template_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def increment_template_usage(self, template_id: UUID) -> bool:
        """Increment usage count for a template."""
        result = await self.db.execute(
            update(ActivityTemplate)
            .where(ActivityTemplate.id == template_id)
            .values(usage_count=ActivityTemplate.usage_count + 1)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Activity Methods
    async def create_activity(self, activity_data: ActivityCreate) -> Activity:
        """Create a new activity."""
        activity = Activity(**activity_data.model_dump())
        self.db.add(activity)
        
        # Increment template usage count if template is used
        if activity.template_id:
            await self.increment_template_usage(activity.template_id)
        
        await self.db.commit()
        await self.db.refresh(activity)
        return activity
    
    async def get_activity(self, activity_id: UUID) -> Optional[Activity]:
        """Get activity by ID."""
        result = await self.db.execute(
            select(Activity)
            .options(selectinload(Activity.template))
            .where(Activity.id == activity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_activities(
        self,
        activity_type: Optional[str] = None,
        template_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        is_mandatory: Optional[bool] = None,
        is_graded: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Activity]:
        """Get activities with optional filters."""
        query = select(Activity)
        
        if activity_type:
            query = query.where(Activity.activity_type == activity_type)
        if template_id:
            query = query.where(Activity.template_id == template_id)
        if created_by:
            query = query.where(Activity.created_by == created_by)
        if is_mandatory is not None:
            query = query.where(Activity.is_mandatory == is_mandatory)
        if is_graded is not None:
            query = query.where(Activity.is_graded == is_graded)
        if search:
            query = query.where(
                or_(
                    Activity.title.ilike(f"%{search}%"),
                    Activity.description.ilike(f"%{search}%")
                )
            )
        
        query = query.offset(skip).limit(limit).order_by(Activity.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_activity(
        self,
        activity_id: UUID,
        activity_data: ActivityUpdate
    ) -> Optional[Activity]:
        """Update activity."""
        existing = await self.get_activity(activity_id)
        if not existing:
            return None
        
        update_data = activity_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Activity)
            .where(Activity.id == activity_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_activity(activity_id)
    
    async def delete_activity(self, activity_id: UUID) -> bool:
        """Delete activity."""
        result = await self.db.execute(
            delete(Activity).where(Activity.id == activity_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    # Course Activity Methods
    async def create_course_activity(self, course_activity_data: CourseActivityCreate) -> CourseActivity:
        """Create a new course activity."""
        course_activity = CourseActivity(**course_activity_data.model_dump())
        self.db.add(course_activity)
        await self.db.commit()
        await self.db.refresh(course_activity)
        return course_activity
    
    async def get_course_activity(self, course_activity_id: UUID) -> Optional[CourseActivity]:
        """Get course activity by ID."""
        result = await self.db.execute(
            select(CourseActivity)
            .options(selectinload(CourseActivity.activity))
            .where(CourseActivity.id == course_activity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_course_activities(
        self,
        course_id: UUID,
        module_id: Optional[UUID] = None,
        is_required: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseActivity]:
        """Get activities for a course ordered by sequence."""
        query = select(CourseActivity).where(CourseActivity.course_id == course_id)
        
        if module_id:
            query = query.where(CourseActivity.module_id == module_id)
        if is_required is not None:
            query = query.where(CourseActivity.is_required == is_required)
        
        query = query.offset(skip).limit(limit).order_by(CourseActivity.order_sequence.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_course_activity(
        self,
        course_activity_id: UUID,
        course_activity_data: Dict[str, Any]
    ) -> Optional[CourseActivity]:
        """Update course activity."""
        existing = await self.get_course_activity(course_activity_id)
        if not existing:
            return None
        
        await self.db.execute(
            update(CourseActivity)
            .where(CourseActivity.id == course_activity_id)
            .values(**course_activity_data)
        )
        await self.db.commit()
        
        return await self.get_course_activity(course_activity_id)
    
    async def delete_course_activity(self, course_activity_id: UUID) -> bool:
        """Delete course activity."""
        result = await self.db.execute(
            delete(CourseActivity).where(CourseActivity.id == course_activity_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def reorder_course_activities(
        self,
        course_id: UUID,
        activity_order: List[Dict[str, Any]]
    ) -> bool:
        """Reorder activities in a course."""
        try:
            for item in activity_order:
                await self.db.execute(
                    update(CourseActivity)
                    .where(
                        and_(
                            CourseActivity.id == item["course_activity_id"],
                            CourseActivity.course_id == course_id
                        )
                    )
                    .values(order_sequence=item["order_sequence"])
                )
            
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    # Activity Analytics
    async def get_template_analytics(self, template_id: UUID) -> Dict[str, Any]:
        """Get analytics for an activity template."""
        template = await self.get_activity_template(template_id)
        if not template:
            return {"error": "Template not found"}
        
        # Get activities created from this template
        result = await self.db.execute(
            select(Activity).where(Activity.template_id == template_id)
        )
        activities = result.scalars().all()
        
        # Get course activities using this template
        activity_ids = [a.id for a in activities]
        if activity_ids:
            result = await self.db.execute(
                select(CourseActivity).where(CourseActivity.activity_id.in_(activity_ids))
            )
            course_activities = result.scalars().all()
        else:
            course_activities = []
        
        return {
            "template_id": str(template_id),
            "template_name": template.name,
            "usage_stats": {
                "total_usage_count": template.usage_count,
                "activities_created": len(activities),
                "courses_using": len(set(ca.course_id for ca in course_activities)),
                "average_rating": template.rating
            },
            "activity_types": {
                "mandatory": len([a for a in activities if a.is_mandatory]),
                "optional": len([a for a in activities if not a.is_mandatory]),
                "graded": len([a for a in activities if a.is_graded]),
                "ungraded": len([a for a in activities if not a.is_graded])
            }
        }
    
    async def get_course_activity_summary(self, course_id: UUID) -> Dict[str, Any]:
        """Get activity summary for a course."""
        course_activities = await self.get_course_activities(course_id, limit=1000)
        
        total_activities = len(course_activities)
        required_activities = len([ca for ca in course_activities if ca.is_required])
        graded_activities = len([ca for ca in course_activities if ca.activity and ca.activity.is_graded])
        
        # Calculate total weight
        total_weight = sum(ca.weight_in_grade for ca in course_activities if ca.weight_in_grade)
        
        # Activity type breakdown
        activity_types = {}
        for ca in course_activities:
            if ca.activity:
                activity_type = ca.activity.activity_type
                activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        return {
            "course_id": str(course_id),
            "activity_stats": {
                "total_activities": total_activities,
                "required_activities": required_activities,
                "optional_activities": total_activities - required_activities,
                "graded_activities": graded_activities,
                "total_grade_weight": total_weight
            },
            "activity_type_breakdown": activity_types
        }