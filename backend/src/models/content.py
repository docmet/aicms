from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.database import Base


class ContentSection(Base):
    """Content section model for page content."""

    __tablename__ = "content_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_type = Column(String(50), nullable=False)  # hero, about, services, contact
    content = Column(Text, nullable=True)  # Plain text, HTML stripped
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    page = relationship("Page", back_populates="content_sections")

    def __repr__(self) -> str:
        return f"<ContentSection(id={self.id}, type={self.section_type})>"
