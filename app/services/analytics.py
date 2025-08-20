from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.models.analytics import AnalyticsData, UserMetrics, Report
from app.schemas.analytics import (
    AnalyticsDataCreate, ReportCreate, ReportUpdate,
    AnalyticsQuery, AnalyticsAggregation
)


class AnalyticsService:
    """Service for managing analytics data, user metrics, and reports."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Analytics Data Methods
    async def create_analytics_data(self, analytics_data: AnalyticsDataCreate) -> AnalyticsData:
        """Create a new analytics data point."""
        data = AnalyticsData(**analytics_data.model_dump())
        if not data.timestamp:
            data.timestamp = datetime.utcnow()
        
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data
    
    async def bulk_create_analytics_data(
        self,
        analytics_data_list: List[AnalyticsDataCreate],
        batch_id: Optional[UUID] = None
    ) -> List[AnalyticsData]:
        """Create multiple analytics data points at once."""
        data_objects = []
        
        for data_item in analytics_data_list:
            data = AnalyticsData(**data_item.model_dump())
            if not data.timestamp:
                data.timestamp = datetime.utcnow()
            if batch_id:
                data.batch_id = batch_id
            
            data_objects.append(data)
            self.db.add(data)
        
        await self.db.commit()
        
        for data in data_objects:
            await self.db.refresh(data)
        
        return data_objects
    
    async def get_analytics_data(
        self,
        query_params: AnalyticsQuery
    ) -> List[AnalyticsData]:
        """Get analytics data based on query parameters."""
        query = select(AnalyticsData).where(
            and_(
                AnalyticsData.timestamp >= query_params.start_date,
                AnalyticsData.timestamp <= query_params.end_date
            )
        )
        
        if query_params.metric_types:
            query = query.where(AnalyticsData.metric_type.in_(query_params.metric_types))
        
        if query_params.user_ids:
            query = query.where(AnalyticsData.user_id.in_(query_params.user_ids))
        
        if query_params.course_ids:
            query = query.where(AnalyticsData.course_id.in_(query_params.course_ids))
        
        if query_params.filters:
            for key, value in query_params.filters.items():
                if hasattr(AnalyticsData, key):
                    query = query.where(getattr(AnalyticsData, key) == value)
        
        if query_params.offset:
            query = query.offset(query_params.offset)
        
        if query_params.limit:
            query = query.limit(query_params.limit)
        
        query = query.order_by(AnalyticsData.timestamp.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_analytics_aggregation(
        self,
        query_params: AnalyticsQuery,
        aggregation: AnalyticsAggregation
    ) -> Dict[str, Any]:
        """Get aggregated analytics data."""
        base_query = select(AnalyticsData).where(
            and_(
                AnalyticsData.timestamp >= query_params.start_date,
                AnalyticsData.timestamp <= query_params.end_date,
                AnalyticsData.metric_type == aggregation.metric_type
            )
        )
        
        if query_params.user_ids:
            base_query = base_query.where(AnalyticsData.user_id.in_(query_params.user_ids))
        
        if query_params.course_ids:
            base_query = base_query.where(AnalyticsData.course_id.in_(query_params.course_ids))
        
        # Apply aggregation function
        if aggregation.aggregation_function == "sum":
            agg_func = func.sum(AnalyticsData.value)
        elif aggregation.aggregation_function == "avg":
            agg_func = func.avg(AnalyticsData.value)
        elif aggregation.aggregation_function == "count":
            agg_func = func.count(AnalyticsData.id)
        elif aggregation.aggregation_function == "min":
            agg_func = func.min(AnalyticsData.value)
        elif aggregation.aggregation_function == "max":
            agg_func = func.max(AnalyticsData.value)
        else:
            agg_func = func.count(AnalyticsData.id)
        
        if aggregation.group_by:
            if hasattr(AnalyticsData, aggregation.group_by):
                group_column = getattr(AnalyticsData, aggregation.group_by)
                query = select(group_column, agg_func, func.count(AnalyticsData.id)).select_from(base_query.subquery()).group_by(group_column)
                
                result = await self.db.execute(query)
                rows = result.fetchall()
                
                return {
                    "metric_type": aggregation.metric_type,
                    "aggregation_function": aggregation.aggregation_function,
                    "group_by": aggregation.group_by,
                    "results": [
                        {
                            "group_value": str(row[0]),
                            "aggregated_value": float(row[1]) if row[1] else 0,
                            "count": int(row[2])
                        }
                        for row in rows
                    ]
                }
        else:
            query = select(agg_func, func.count(AnalyticsData.id)).select_from(base_query.subquery())
            result = await self.db.execute(query)
            row = result.fetchone()
            
            return {
                "metric_type": aggregation.metric_type,
                "aggregation_function": aggregation.aggregation_function,
                "aggregated_value": float(row[0]) if row[0] else 0,
                "count": int(row[1])
            }
    
    # User Metrics Methods
    async def get_user_metrics(
        self,
        user_id: UUID,
        period_type: str = "daily",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserMetrics]:
        """Get user metrics for a specific period."""
        query = select(UserMetrics).where(
            and_(
                UserMetrics.user_id == user_id,
                UserMetrics.period_type == period_type
            )
        )
        
        if start_date:
            query = query.where(UserMetrics.date >= start_date)
        if end_date:
            query = query.where(UserMetrics.date <= end_date)
        
        query = query.offset(skip).limit(limit).order_by(UserMetrics.date.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_or_update_user_metrics(
        self,
        user_id: UUID,
        date: datetime,
        period_type: str,
        metrics_data: Dict[str, Any]
    ) -> UserMetrics:
        """Create or update user metrics for a specific date and period."""
        # Check if metrics already exist
        result = await self.db.execute(
            select(UserMetrics).where(
                and_(
                    UserMetrics.user_id == user_id,
                    UserMetrics.date == date.date(),
                    UserMetrics.period_type == period_type
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing metrics
            for key, value in metrics_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new metrics
            metrics = UserMetrics(
                user_id=user_id,
                date=date,
                period_type=period_type,
                **metrics_data
            )
            self.db.add(metrics)
            await self.db.commit()
            await self.db.refresh(metrics)
            return metrics
    
    # Report Methods
    async def create_report(self, report_data: ReportCreate) -> Report:
        """Create a new report."""
        report = Report(**report_data.model_dump())
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report
    
    async def get_report(self, report_id: UUID) -> Optional[Report]:
        """Get report by ID."""
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_reports(
        self,
        report_type: Optional[str] = None,
        report_category: Optional[str] = None,
        created_by: Optional[UUID] = None,
        is_scheduled: Optional[bool] = None,
        is_public: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Report]:
        """Get reports with optional filters."""
        query = select(Report)
        
        if report_type:
            query = query.where(Report.report_type == report_type)
        if report_category:
            query = query.where(Report.report_category == report_category)
        if created_by:
            query = query.where(Report.created_by == created_by)
        if is_scheduled is not None:
            query = query.where(Report.is_scheduled == is_scheduled)
        if is_public is not None:
            query = query.where(Report.is_public == is_public)
        
        query = query.offset(skip).limit(limit).order_by(Report.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_report(
        self,
        report_id: UUID,
        report_data: ReportUpdate
    ) -> Optional[Report]:
        """Update report."""
        existing = await self.get_report(report_id)
        if not existing:
            return None
        
        update_data = report_data.model_dump(exclude_unset=True)
        
        await self.db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_report(report_id)
    
    async def delete_report(self, report_id: UUID) -> bool:
        """Delete report."""
        result = await self.db.execute(
            delete(Report).where(Report.id == report_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def generate_report(self, report_id: UUID) -> Dict[str, Any]:
        """Generate a report based on its configuration."""
        report = await self.get_report(report_id)
        if not report:
            return {"error": "Report not found"}
        
        # Update report status
        await self.db.execute(
            update(Report)
            .where(Report.id == report_id)
            .values(
                generation_status="generating",
                last_generated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        try:
            # Generate report based on type
            if report.report_type == "performance":
                report_data = await self._generate_performance_report(report)
            elif report.report_type == "engagement":
                report_data = await self._generate_engagement_report(report)
            elif report.report_type == "progress":
                report_data = await self._generate_progress_report(report)
            else:
                report_data = await self._generate_custom_report(report)
            
            # Update report as completed
            await self.db.execute(
                update(Report)
                .where(Report.id == report_id)
                .values(generation_status="completed")
            )
            await self.db.commit()
            
            return report_data
            
        except Exception as e:
            # Update report as failed
            await self.db.execute(
                update(Report)
                .where(Report.id == report_id)
                .values(generation_status="failed")
            )
            await self.db.commit()
            
            return {"error": f"Report generation failed: {str(e)}"}
    
    async def _generate_performance_report(self, report: Report) -> Dict[str, Any]:
        """Generate performance report."""
        parameters = report.parameters
        
        # Get performance metrics
        query_params = AnalyticsQuery(
            start_date=datetime.fromisoformat(parameters.get("start_date")),
            end_date=datetime.fromisoformat(parameters.get("end_date")),
            metric_types=["assessment_score", "quiz_score", "assignment_grade"],
            user_ids=parameters.get("user_ids"),
            course_ids=parameters.get("course_ids")
        )
        
        analytics_data = await self.get_analytics_data(query_params)
        
        # Calculate performance metrics
        scores = [d.value for d in analytics_data if d.value is not None]
        
        return {
            "report_id": str(report.id),
            "report_name": report.name,
            "generated_at": datetime.utcnow().isoformat(),
            "performance_summary": {
                "total_assessments": len(analytics_data),
                "average_score": sum(scores) / len(scores) if scores else 0,
                "highest_score": max(scores) if scores else 0,
                "lowest_score": min(scores) if scores else 0,
                "pass_rate": len([s for s in scores if s >= 70]) / len(scores) * 100 if scores else 0
            },
            "detailed_data": [
                {
                    "user_id": str(d.user_id) if d.user_id else None,
                    "course_id": str(d.course_id) if d.course_id else None,
                    "metric_type": d.metric_type,
                    "score": d.value,
                    "timestamp": d.timestamp.isoformat()
                }
                for d in analytics_data
            ]
        }
    
    async def _generate_engagement_report(self, report: Report) -> Dict[str, Any]:
        """Generate engagement report."""
        parameters = report.parameters
        
        query_params = AnalyticsQuery(
            start_date=datetime.fromisoformat(parameters.get("start_date")),
            end_date=datetime.fromisoformat(parameters.get("end_date")),
            metric_types=["page_view", "video_watch", "forum_post", "discussion_reply"],
            user_ids=parameters.get("user_ids"),
            course_ids=parameters.get("course_ids")
        )
        
        analytics_data = await self.get_analytics_data(query_params)
        
        # Calculate engagement metrics
        unique_users = len(set(d.user_id for d in analytics_data if d.user_id))
        total_interactions = len(analytics_data)
        
        return {
            "report_id": str(report.id),
            "report_name": report.name,
            "generated_at": datetime.utcnow().isoformat(),
            "engagement_summary": {
                "unique_active_users": unique_users,
                "total_interactions": total_interactions,
                "average_interactions_per_user": total_interactions / unique_users if unique_users > 0 else 0
            },
            "interaction_breakdown": self._calculate_interaction_breakdown(analytics_data)
        }
    
    async def _generate_progress_report(self, report: Report) -> Dict[str, Any]:
        """Generate progress report."""
        # This would integrate with the progress service
        return {
            "report_id": str(report.id),
            "report_name": report.name,
            "generated_at": datetime.utcnow().isoformat(),
            "progress_summary": {
                "total_courses": 0,
                "completed_courses": 0,
                "in_progress_courses": 0,
                "completion_rate": 0
            }
        }
    
    async def _generate_custom_report(self, report: Report) -> Dict[str, Any]:
        """Generate custom report."""
        return {
            "report_id": str(report.id),
            "report_name": report.name,
            "generated_at": datetime.utcnow().isoformat(),
            "message": "Custom report generation not implemented"
        }
    
    def _calculate_interaction_breakdown(self, analytics_data: List[AnalyticsData]) -> Dict[str, int]:
        """Calculate breakdown of interactions by type."""
        breakdown = {}
        for data in analytics_data:
            metric_type = data.metric_type
            breakdown[metric_type] = breakdown.get(metric_type, 0) + 1
        return breakdown
    
    # Dashboard Analytics
    async def get_dashboard_analytics(
        self,
        user_id: Optional[UUID] = None,
        course_id: Optional[UUID] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get analytics data for dashboard display."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        query_params = AnalyticsQuery(
            start_date=start_date,
            end_date=end_date,
            user_ids=[user_id] if user_id else None,
            course_ids=[course_id] if course_id else None
        )
        
        analytics_data = await self.get_analytics_data(query_params)
        
        # Calculate key metrics
        total_interactions = len(analytics_data)
        unique_users = len(set(d.user_id for d in analytics_data if d.user_id))
        unique_courses = len(set(d.course_id for d in analytics_data if d.course_id))
        
        # Daily activity trend
        daily_activity = {}
        for data in analytics_data:
            date_key = data.timestamp.date().isoformat()
            daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
        
        return {
            "period": f"Last {days_back} days",
            "summary": {
                "total_interactions": total_interactions,
                "unique_users": unique_users,
                "unique_courses": unique_courses,
                "average_daily_activity": total_interactions / days_back
            },
            "daily_activity": daily_activity,
            "top_metrics": self._get_top_metrics(analytics_data)
        }
    
    def _get_top_metrics(self, analytics_data: List[AnalyticsData]) -> Dict[str, List[Dict[str, Any]]]:
        """Get top metrics from analytics data."""
        # Top metric types
        metric_counts = {}
        for data in analytics_data:
            metric_type = data.metric_type
            metric_counts[metric_type] = metric_counts.get(metric_type, 0) + 1
        
        top_metrics = sorted(metric_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "top_metric_types": [
                {"metric_type": metric, "count": count}
                for metric, count in top_metrics
            ]
        }