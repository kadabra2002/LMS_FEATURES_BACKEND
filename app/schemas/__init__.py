from .progress import (
    ProgressTrackingCreate, ProgressTrackingUpdate, ProgressTrackingResponse,
    UserAssessmentCreate, UserAssessmentUpdate, UserAssessmentResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceResponse
)
from .learning_path import (
    LearningPathCreate, LearningPathUpdate, LearningPathResponse,
    LearningPathCourseCreate, LearningPathCourseResponse,
    UserLearningPathCreate, UserLearningPathUpdate, UserLearningPathResponse
)
from .assessment import (
    AssessmentCreate, AssessmentUpdate, AssessmentResponse,
    QuestionCreate, QuestionUpdate, QuestionResponse,
    UserAnswerCreate, UserAnswerResponse,
    FeedbackCreate, FeedbackResponse
)
from .target import (
    TargetCreate, TargetUpdate, TargetResponse,
    ReminderCreate, ReminderUpdate, ReminderResponse
)
from .schedule import (
    CourseScheduleCreate, CourseScheduleUpdate, CourseScheduleResponse,
    UserCourseEnrollmentCreate, UserCourseEnrollmentUpdate, UserCourseEnrollmentResponse
)
from .activity import (
    ActivityTemplateCreate, ActivityTemplateUpdate, ActivityTemplateResponse,
    ActivityCreate, ActivityUpdate, ActivityResponse,
    CourseActivityCreate, CourseActivityResponse
)
from .automation import (
    AutomationRuleCreate, AutomationRuleUpdate, AutomationRuleResponse,
    AutomationExecutionResponse, AutomationLogResponse
)
from .localization import (
    LanguageCreate, LanguageUpdate, LanguageResponse,
    TranslationCreate, TranslationUpdate, TranslationResponse
)
from .analytics import (
    AnalyticsDataCreate, AnalyticsDataResponse,
    UserMetricsResponse, ReportCreate, ReportUpdate, ReportResponse
)

__all__ = [
    # Progress tracking schemas
    "ProgressTrackingCreate", "ProgressTrackingUpdate", "ProgressTrackingResponse",
    "UserAssessmentCreate", "UserAssessmentUpdate", "UserAssessmentResponse", 
    "AttendanceCreate", "AttendanceUpdate", "AttendanceResponse",
    
    # Learning path schemas
    "LearningPathCreate", "LearningPathUpdate", "LearningPathResponse",
    "LearningPathCourseCreate", "LearningPathCourseResponse",
    "UserLearningPathCreate", "UserLearningPathUpdate", "UserLearningPathResponse",
    
    # Assessment schemas
    "AssessmentCreate", "AssessmentUpdate", "AssessmentResponse",
    "QuestionCreate", "QuestionUpdate", "QuestionResponse",
    "UserAnswerCreate", "UserAnswerResponse",
    "FeedbackCreate", "FeedbackResponse",
    
    # Target schemas
    "TargetCreate", "TargetUpdate", "TargetResponse",
    "ReminderCreate", "ReminderUpdate", "ReminderResponse",
    
    # Schedule schemas
    "CourseScheduleCreate", "CourseScheduleUpdate", "CourseScheduleResponse",
    "UserCourseEnrollmentCreate", "UserCourseEnrollmentUpdate", "UserCourseEnrollmentResponse",
    
    # Activity schemas
    "ActivityTemplateCreate", "ActivityTemplateUpdate", "ActivityTemplateResponse",
    "ActivityCreate", "ActivityUpdate", "ActivityResponse",
    "CourseActivityCreate", "CourseActivityResponse",
    
    # Automation schemas
    "AutomationRuleCreate", "AutomationRuleUpdate", "AutomationRuleResponse",
    "AutomationExecutionResponse", "AutomationLogResponse",
    
    # Localization schemas
    "LanguageCreate", "LanguageUpdate", "LanguageResponse",
    "TranslationCreate", "TranslationUpdate", "TranslationResponse",
    
    # Analytics schemas
    "AnalyticsDataCreate", "AnalyticsDataResponse",
    "UserMetricsResponse", "ReportCreate", "ReportUpdate", "ReportResponse"
]