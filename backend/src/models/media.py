import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class MediaFile(Base):
    """A media file (image or document) uploaded for a site."""

    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(500), nullable=False, unique=True)
    url = Column(String(1000), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_type = Column(String(20), nullable=False)  # "image" | "document"
    size_bytes = Column(Integer, nullable=False)

    # Image-only metadata
    alt_text = Column(String(500), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    site = relationship("Site", back_populates="media_files")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<MediaFile(id={self.id}, site_id={self.site_id}, key={self.storage_key})>"
