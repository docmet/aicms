from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.database import Base


class Theme(Base):
    """Theme model for site themes."""

    __tablename__ = "themes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    config = Column(JSON, nullable=True)  # TailwindCSS theme config
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Theme(id={self.id}, slug={self.slug}, name={self.name})>"
