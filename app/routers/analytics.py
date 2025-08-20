from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.schemas.analytics import (
    AnalyticsDataCreate, AnalyticsDataResponse,
    UserMetricsResponse, ReportCreate, ReportUpdate, ReportResponse,
    AnalyticsQuery, AnalyticsAggregation
)
from app.services.analytics import AnalyticsService

router = APIRouter()


# Analytics Data Endpoints
@router.post("/data", response_model=AnalyticsDataResponse)
async def create_analytics_data(
    analytics_data: AnalyticsDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new analytics data point."""
    service = AnalyticsService(db)
    return await service.create_analytics_data(analytics_data)


@router.post("/data/bulk", response_model=List[AnalyticsDataResponse])
async def bulk_create_analytics_data(
    analytics_data_list: List[AnalyticsDataCreate],
    batch_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple analytics data points at once."""
    service = AnalyticsService(db)
    return await service.bulk_create_analytics_data(analytics_data_list, batch_id)


@router.post("/data/query", response_model=List[AnalyticsDataResponse])
async def get_analytics_data(
    query_params: AnalyticsQuery = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics data based on query parameters."""
    service = AnalyticsService(db)
    return await service.get_analytics_data(query_params)


@router.post("/data/aggregate")
async def get_analytics_aggregation(
    query_params: AnalyticsQuery = Body(...),
    aggregation: AnalyticsAggregation = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated analytics data."""
    service = AnalyticsService(db)
    return await service.get_analytics_aggregation(query_params, aggregation)


# User Metrics Endpoints
@router.get("/users/{user_id}/metrics", response_model=List[UserMetricsResponse])
async def get_user_metrics(
    user_id: UUID,
    period_type: str = Query("daily"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get user metrics for a specific period."""
    service = AnalyticsService(db)
    return await service.get_user_metrics(
        user_id=user_id,
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )


@router.post("/users/{user_id}/metrics", response_model=UserMetricsResponse)
async def create_or_update_user_metrics(
    user_id: UUID,
    date: datetime = Body(...),
    period_type: str = Body(...),
    metrics_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Create or update user metrics for a specific date and period."""
    service = AnalyticsService(db)
    return await service.create_or_update_user_metrics(
        user_id=user_id,
        date=date,
        period_type=period_type,
        metrics_data=metrics_data
    )


# Report Endpoints
@router.post("/reports", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new report."""
    service = AnalyticsService(db)
    return await service.create_report(report_data)


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get report by ID."""
    service = AnalyticsService(db)
    report = await service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    report_type: Optional[str] = Query(None),
    report_category: Optional[str] = Query(None),
    created_by: Optional[UUID] = Query(None),
    is_scheduled: Optional[bool] = Query(None),
    is_public: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get reports with optional filters."""
    service = AnalyticsService(db)
    return await service.get_reports(
        report_type=report_type,
        report_category=report_category,
        created_by=created_by,
        is_scheduled=is_scheduled,
        is_public=is_public,
        skip=skip,
        limit=limit
    )


@router.put("/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    report_data: ReportUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update report."""
    service = AnalyticsService(db)
    report = await service.update_report(report_id, report_data)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete report."""
    service = AnalyticsService(db)
    success = await service.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}


@router.post("/reports/{report_id}/generate")
async def generate_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Generate a report based on its configuration."""
    service = AnalyticsService(db)
    return await service.generate_report(report_id)


# Dashboard Analytics
@router.get("/dashboard")
async def get_dashboard_analytics(
    user_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics data for dashboard display."""
    service = AnalyticsService(db)
    return await service.get_dashboard_analytics(
        user_id=user_id,
        course_id=course_id,
        days_back=days_back
    )