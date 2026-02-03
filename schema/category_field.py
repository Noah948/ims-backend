from pydantic import BaseModel, validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Literal


# ----- Create -----
class CategoryFieldCreate(BaseModel):
    field_name: str
    field_type: Literal["text", "number", "date", "dropdown"]
    dropdown_options: Optional[List[str]] = None

    @validator("dropdown_options", always=True)
    def check_dropdown_options(cls, v, values):
        if values.get("field_type") == "dropdown" and not v:
            raise ValueError("dropdown_options must be provided for dropdown type")
        return v


# ----- Update -----
class CategoryFieldUpdate(BaseModel):
    field_name: Optional[str] = None
    field_type: Optional[Literal["text", "number", "date", "dropdown"]] = None
    dropdown_options: Optional[List[str]] = None

    @validator("dropdown_options", always=True)
    def check_dropdown_options(cls, v, values):
        if values.get("field_type") == "dropdown" and not v:
            raise ValueError("dropdown_options must be provided for dropdown type")
        return v

# ----- Response -----
class CategoryFieldResponse(BaseModel):
    id: UUID
    category_id: UUID
    field_name: str
    field_type: str
    dropdown_options: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True