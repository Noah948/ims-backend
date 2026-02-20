from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Literal

FieldType = Literal["text", "number", "date"]


class CategoryFieldItem(BaseModel):
    key: str = Field(..., min_length=2, max_length=100)
    type: FieldType


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    fields: Optional[List[CategoryFieldItem]] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    fields: Optional[List[CategoryFieldItem]] = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    fields: Optional[List[CategoryFieldItem]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
