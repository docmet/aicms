import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

MAX_VERSIONS_PER_PAGE = 5


class PageVersion(Base):
    """Snapshot of a page's content at publish time.

    Stores a JSON snapshot of all sections (content_published values).
    Maximum MAX_VERSIONS_PER_PAGE versions are kept per page.
    When the limit is exceeded, the oldest version is deleted.

    Rollback: reverting sets content_draft to the snapshot values.
    The user still needs to publish after a rollback to make it live.
    """

    __tablename__ = "page_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number = Column(Integer, nullable=False)
    snapshot = Column(Text, nullable=False)  # JSON: full page+sections state
    published_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    label = Column(String(255), nullable=True)  # Optional human label

    # Relationships
    page = relationship("Page", back_populates="versions")

    def __repr__(self) -> str:
        return f"<PageVersion(id={self.id}, page_id={self.page_id}, v={self.version_number})>"
