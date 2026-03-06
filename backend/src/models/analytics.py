import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.database import Base


class PageView(Base):
    """Privacy-first pageview — no cookies, no user IDs."""

    __tablename__ = "page_views"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    page_path = Column(String(500), nullable=False)
    referrer = Column(String(500), nullable=True)
    country = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
