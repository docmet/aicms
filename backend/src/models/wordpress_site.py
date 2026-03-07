import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class WordPressSite(Base):
    """WordPress site registration for MCP-based WP content management."""

    __tablename__ = "wordpress_sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    site_url = Column(String(500), nullable=False)
    app_username = Column(String(255), nullable=False)
    app_password_encrypted = Column(String(1000), nullable=False)
    site_name = Column(String(255), nullable=True)
    mcp_token = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # Relationships
    user = relationship("User", back_populates="wordpress_sites")

    def __repr__(self) -> str:
        return f"<WordPressSite(id={self.id}, site_url={self.site_url})>"
