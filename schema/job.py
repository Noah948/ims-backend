from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


# =====================================================
# Base Schema
# =====================================================

class JobBase(BaseModel):
    business_name: str = Field(..., min_length=2)
    title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=10)

    location: Optional[str] = Field(None, min_length=2)
    salary: Optional[str] = Field(None, min_length=2)
    email: Optional[EmailStr] = None
    contact: Optional[str] = None

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        cleaned = v.replace(" ", "").replace("+", "")
        if not cleaned.isdigit():
            raise ValueError("Contact must contain only numbers")

        return v


# =====================================================
# Create
# =====================================================

class JobCreate(JobBase):
    pass


# =====================================================
# Update
# =====================================================

class JobUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2)
    title: Optional[str] = Field(None, min_length=2)
    description: Optional[str] = Field(None, min_length=10)

    location: Optional[str] = Field(None, min_length=2)
    salary: Optional[str] = Field(None, min_length=2)
    email: Optional[EmailStr] = None
    contact: Optional[str] = None

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        cleaned = v.replace(" ", "").replace("+", "")
        if not cleaned.isdigit():
            raise ValueError("Contact must contain only numbers")

        return v


# =====================================================
# Public Response
# =====================================================

class JobResponse(BaseModel):
    id: UUID
    business_name: str
    title: str
    description: str

    location: Optional[str]
    salary: Optional[str]
    email: Optional[EmailStr]
    contact: Optional[str]

    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
