from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class TimestampSchema(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
