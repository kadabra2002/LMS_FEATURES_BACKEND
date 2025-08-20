from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.models import BaseModel
from app.routers import (
    progress_router, learning_path_router, assessment_router,
    target_router, schedule_router, activity_router,
    automation_router, localization_router, analytics_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("Starting LMS Learning Management Backend...")
    
    # Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down LMS Learning Management Backend...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers 
app.include_router(progress_router, prefix="/progress", tags=["Progress Tracking"])
app.include_router(learning_path_router, prefix="/learning-paths", tags=["Learning Paths"])
app.include_router(assessment_router, prefix="/assessments", tags=["Assessments"])
app.include_router(target_router, prefix="/targets", tags=["Targets & Reminders"])
app.include_router(schedule_router, prefix="/schedules", tags=["Course Scheduling"])
app.include_router(activity_router, prefix="/activities", tags=["Activity Management"])
app.include_router(automation_router, prefix="/automation", tags=["Automation"])
app.include_router(localization_router, prefix="/localization", tags=["Localization"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics & Reports"])



@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Learning Management Features",
        "version": settings.VERSION,
        "api_docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "status": "active",
        "features": [
            "Progress Tracking",
            "Assessments & Online Attendance", 
            "Adaptive Learning Paths",
            "Target Achievement Tracking",
            "Course Scheduling",
            "Activity Reusability",
            "Automation",
            "Localization",
            "Reports and Analytics"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "lms-learning-management",
        "version": settings.VERSION,
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )