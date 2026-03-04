"""MCP Client model for AI tools integration."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class MCPClient(Base):
    """MCP Client registration for AI tools."""

    __tablename__ = "mcp_clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    tool_type = Column(String(50), nullable=False)  # claude, chatgpt, cursor
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_used = Column(DateTime(timezone=True), nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional tool-specific data
