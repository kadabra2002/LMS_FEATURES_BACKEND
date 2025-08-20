from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:Ibrahim2002#@localhost/LMS"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LMS Learning Management Features"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis for caching and task queue
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Localization
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "es", "fr", "de", "zh"]
    
    # Analytics
    ANALYTICS_BATCH_SIZE: int = 100
    REPORT_CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"


settings = Settings()