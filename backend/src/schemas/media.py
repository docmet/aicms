from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MediaFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    site_id: UUID
    user_id: UUID | None
    original_filename: str
    storage_key: str
    url: str
    mime_type: str
    file_type: str
    size_bytes: int
    alt_text: str | None
    width: int | None
    height: int | None
    created_at: datetime
