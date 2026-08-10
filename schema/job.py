from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class JobBase(BaseModel):
    title: str = Field(..., min_length=2)
    location: Optional[str] = Field(None, min_length=2)
    salary: Optional[str] = Field(None, min_length=2)
    email: Optional[EmailStr] = None
    contact: str

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("+", "")
        if not cleaned.isdigit():
            raise ValueError("Contact must contain only numbers")
        if len(cleaned) != 10:
            raise ValueError("Contact must be exactly 10 digits")
        return cleaned


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2)
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
        if len(cleaned) != 10:
            raise ValueError("Contact must be exactly 10 digits")
        return cleaned


class JobResponse(BaseModel):
    id: UUID
    business_id: UUID
    title: str
    location: Optional[str]
    salary: Optional[str]
    email: Optional[EmailStr]
    contact: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True