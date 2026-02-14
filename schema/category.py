from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


# =====================================================
# Base
# =====================================================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


# =====================================================
# Create
# =====================================================

class CategoryCreate(CategoryBase):
    pass


# =====================================================
# Update
# =====================================================

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)


# =====================================================
# Public Response
# =====================================================

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
