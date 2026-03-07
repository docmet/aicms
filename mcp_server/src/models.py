from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class MCPClient(Base):
    """MCP Client registration for AI tools"""

    __tablename__ = "mcp_clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # No FK - just store the ID
    tool_type = Column(String(50), nullable=False)  # claude, chatgpt, cursor
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional tool-specific data


class WordPressSite(Base):
    """Read-only mirror of backend wordpress_sites — used only for mcp_token auth."""

    __tablename__ = "wordpress_sites"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    mcp_token = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
