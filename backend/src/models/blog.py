import uuid
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class BlogPost(Base):
    """A blog post belonging to a site."""

    __tablename__ = "blog_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slug = Column(String(200), nullable=False)
    title = Column(String(500), nullable=False)
    excerpt = Column(Text, nullable=True)
    body = Column(Text, nullable=False, default="")
    author_name = Column(String(200), nullable=True)
    cover_image_url = Column(String(1000), nullable=True)
    tags: Any = Column(JSON, nullable=False, default=list)

    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("site_id", "slug", name="uq_blog_posts_site_slug"),
    )

    # Relationships
    site = relationship("Site", back_populates="blog_posts")

    @property
    def is_published(self) -> bool:
        return self.published_at is not None

    def __repr__(self) -> str:
        return f"<BlogPost(id={self.id}, site_id={self.site_id}, slug={self.slug})>"
