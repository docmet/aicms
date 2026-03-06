import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Page(Base):
    """Page within a site.

    Pages hold ordered ContentSections. Publishing a page snapshots all section
    content_draft values into content_published and creates a PageVersion record.
    The public site renders content_published; drafts are only visible to the owner.
    """

    __tablename__ = "pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    last_published_at = Column(DateTime(timezone=True), nullable=True)  # set on each publish
    scheduled_at = Column(DateTime(timezone=True), nullable=True)  # future publish datetime (UTC)
    order = Column(Integer, default=0, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    site = relationship("Site", back_populates="pages")
    content_sections = relationship(
        "ContentSection", back_populates="page", cascade="all, delete-orphan"
    )
    versions = relationship(
        "PageVersion",
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="PageVersion.version_number.desc()",
    )

    def __repr__(self) -> str:
        return f"<Page(id={self.id}, title={self.title}, slug={self.slug})>"
