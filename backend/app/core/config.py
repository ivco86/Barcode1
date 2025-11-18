from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings with environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://posuser:localpass@postgres:5432/posdb"

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # JWT
    JWT_SECRET: str = "local-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Feature Flags (Локално vs Cloud)
    STRIPE_ENABLED: bool = False
    EMAIL_ENABLED: bool = False
    SUBSCRIPTION_CHECKS_ENABLED: bool = False

    # Stripe (празно за локално)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
