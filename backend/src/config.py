from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql+asyncpg://aicms:aicms_password@localhost:5432/aicms"

    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    # Application
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    domain: str = "aicms.docmet.systems"

    # Stripe (billing)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""
    stripe_agency_price_id: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
