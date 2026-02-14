from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Literal


# =====================================================
# Enums
# =====================================================

FieldType = Literal["text", "number", "date", "dropdown"]


# =====================================================
# Base
# =====================================================

class CategoryFieldBase(BaseModel):
    field_name: str = Field(..., min_length=2, max_length=100)
    field_type: FieldType
    dropdown_options: Optional[List[str]] = None

    @field_validator("dropdown_options")
    @classmethod
    def validate_dropdown_options(cls, v, info):
        field_type = info.data.get("field_type")

        if field_type == "dropdown":
            if not v or len(v) == 0:
                raise ValueError("dropdown_options must be provided for dropdown type")

            # Remove empty strings and trim whitespace
            cleaned = [opt.strip() for opt in v if opt.strip()]
            if len(cleaned) == 0:
                raise ValueError("dropdown_options cannot contain empty values")

            return cleaned

        # If not dropdown → ensure no options passed
        if v:
            raise ValueError("dropdown_options allowed only for dropdown type")

        return None


# =====================================================
# Create
# =====================================================

class CategoryFieldCreate(CategoryFieldBase):
    pass


# =====================================================
# Update
# =====================================================

class CategoryFieldUpdate(BaseModel):
    field_name: Optional[str] = Field(None, min_length=2, max_length=100)
    field_type: Optional[FieldType] = None
    dropdown_options: Optional[List[str]] = None

    @field_validator("dropdown_options")
    @classmethod
    def validate_dropdown_options(cls, v, info):
        field_type = info.data.get("field_type")

        if field_type == "dropdown":
            if not v or len(v) == 0:
                raise ValueError("dropdown_options must be provided for dropdown type")

            cleaned = [opt.strip() for opt in v if opt.strip()]
            if len(cleaned) == 0:
                raise ValueError("dropdown_options cannot contain empty values")

            return cleaned

        if v:
            raise ValueError("dropdown_options allowed only for dropdown type")

        return None


# =====================================================
# Response
# =====================================================

class CategoryFieldResponse(BaseModel):
    id: UUID
    category_id: UUID
    field_name: str
    field_type: FieldType
    dropdown_options: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
