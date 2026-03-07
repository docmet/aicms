from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql+asyncpg://aicms:aicms_password@localhost:5432/aicms"

    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # Application
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    domain: str = "aicms.docmet.systems"

    # Stripe (billing)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""
    stripe_agency_price_id: str = ""

    # Email (SMTP)
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@mystorey.io"
    smtp_tls: bool = False  # True for port 587 STARTTLS (staging/prod)

    # Storage (media uploads)
    storage_backend: str = "local"  # "local" | "r2"
    local_upload_path: str = "/app/uploads"
    upload_base_url: str = "http://localhost/uploads"  # URL prefix for local files
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_url: str = ""  # e.g. https://media.mystorey.io
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
