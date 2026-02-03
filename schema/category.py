from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Category Fields ----------

class CategoryFieldCreate(BaseModel):
    field_name: str
    field_type: str  # text | number | date | dropdown
    dropdown_options: list[str] | None = None

class CategoryFieldResponse(BaseModel):
    id: UUID
    field_name: str
    field_type: str
    dropdown_options: list[str] | None

    class Config:
        from_attributes = True
