from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MCPClientCreate(BaseModel):
    """Create a new MCP client"""
    name: str = Field(..., min_length=1, max_length=255)
    user_id: UUID
    tool_type: str = Field(..., regex="^(claude|chatgpt|cursor)$")
    metadata: Optional[Dict[str, Any]] = None


class MCPClientResponse(BaseModel):
    """MCP client response"""
    id: UUID
    name: str
    tool_type: str
    token: str
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
