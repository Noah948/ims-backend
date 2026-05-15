from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Literal, Dict, Any


# =========================================================
# FIELD TYPES
# =========================================================

FieldType = Literal[
    "text",
    "number",
    "date"
]


# =========================================================
# FIELD SCHEMAS
# =========================================================

class CategoryFieldBase(BaseModel):

    key: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    type: FieldType

    # Optional because backend auto-manages order now
    order: Optional[int] = Field(
        default=None,
        ge=1
    )

    required: Optional[bool] = False

    meta: Optional[Dict[str, Any]] = {}


# =========================================================
# CREATE FIELD
# =========================================================

class CategoryFieldCreate(CategoryFieldBase):
    pass


# =========================================================
# FIELD RESPONSE
# =========================================================

class CategoryFieldResponse(CategoryFieldBase):

    id: UUID


# =========================================================
# UPDATE FIELD
# =========================================================

class CategoryFieldUpdate(BaseModel):

    key: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )

    type: Optional[FieldType] = None

    # Optional manual order update if needed
    order: Optional[int] = Field(
        None,
        ge=1
    )

    required: Optional[bool] = None

    meta: Optional[Dict[str, Any]] = None


# =========================================================
# REORDER FIELDS
# =========================================================

class CategoryFieldReorder(BaseModel):

    ordered_field_ids: List[str]


# =========================================================
# CATEGORY BASE
# =========================================================

class CategoryBase(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )


# =========================================================
# CREATE CATEGORY
# =========================================================

class CategoryCreate(CategoryBase):

    fields: Optional[List[CategoryFieldCreate]] = []


# =========================================================
# UPDATE CATEGORY
# =========================================================

class CategoryUpdate(BaseModel):

    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )


# =========================================================
# CATEGORY RESPONSE
# =========================================================

class CategoryResponse(BaseModel):

    id: UUID

    name: str

    fields: Optional[List[CategoryFieldResponse]] = []

    created_at: datetime

    updated_at: Optional[datetime]

    class Config:
        from_attributes = True