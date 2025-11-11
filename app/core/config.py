"""
Configuration Module
KHÁI NIỆM: Centralized configuration sử dụng Pydantic Settings
- Tự động load từ .env file
- Type validation cho config values
- Default values cho development
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings

    VÍ DỤ: Khi bạn set DATABASE_URL trong .env file,
    Pydantic tự động load và validate nó
    """
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/user_service_db"

    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 300  # Cache TTL: 5 phút (300 giây)

    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    PROJECT_NAME: str = "User Management Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance - dùng chung trong toàn bộ app
settings = Settings()
