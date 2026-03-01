from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    entity_type: str
    entity_id: Optional[UUID]
    operation: str
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True