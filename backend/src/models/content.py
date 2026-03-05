import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class ContentSection(Base):
    """Content section within a page.

    Each section has a type (hero, features, etc.) and separate draft/published
    content stored as JSON strings. The public site always renders content_published.
    Edits (by user or AI) go to content_draft until the page is published.
    """

    __tablename__ = "content_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_type = Column(String(50), nullable=False)  # hero, features, testimonials, about, contact, cta, pricing, custom
    content_draft = Column(Text, nullable=True)     # JSON string being edited (not yet public)
    content_published = Column(Text, nullable=True) # JSON string visible to public (set on publish)
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
    page = relationship("Page", back_populates="content_sections")

    @property
    def has_unpublished_changes(self) -> bool:
        """True if draft differs from published (unpublished edits exist)."""
        return self.content_draft != self.content_published  # type: ignore[return-value]

    def __repr__(self) -> str:
        return f"<ContentSection(id={self.id}, type={self.section_type})>"
