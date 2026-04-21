from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Literal, Dict, Any

FieldType = Literal["text", "number", "date"]


# =========================
# 🔹 Field Schemas
# =========================

class CategoryFieldBase(BaseModel):
    key: str = Field(..., min_length=2, max_length=100)
    type: FieldType
    order: int = Field(..., ge=0)
    required: Optional[bool] = False
    meta: Optional[Dict[str, Any]] = None


# ✅ Used when creating a field (NO id)
class CategoryFieldCreate(CategoryFieldBase):
    pass


# ✅ Used in responses (WITH id)
class CategoryFieldResponse(CategoryFieldBase):
    id: UUID


# ✅ Used when updating a field (partial update)
class CategoryFieldUpdate(BaseModel):
    key: Optional[str] = Field(None, min_length=2, max_length=100)
    type: Optional[FieldType] = None
    order: Optional[int] = Field(None, ge=0)
    required: Optional[bool] = None
    meta: Optional[Dict[str, Any]] = None


# =========================
# 🔹 Category Schemas
# =========================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class CategoryCreate(CategoryBase):
    fields: Optional[List[CategoryFieldCreate]] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    # ❌ We REMOVE direct fields update here
    # Fields should be handled via dedicated routes


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    fields: Optional[List[CategoryFieldResponse]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True