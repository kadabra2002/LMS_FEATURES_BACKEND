from .progress import router as progress_router
from .learning_path import router as learning_path_router
from .assessment import router as assessment_router
from .target import router as target_router
from .schedule import router as schedule_router
from .activity import router as activity_router
from .automation import router as automation_router
from .localization import router as localization_router
from .analytics import router as analytics_router

__all__ = [
    "progress_router",
    "learning_path_router",
    "assessment_router",
    "target_router",
    "schedule_router",
    "activity_router",
    "automation_router",
    "localization_router",
    "analytics_router"
]