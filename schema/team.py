from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal


# =====================================================
# Allowed Roles
# =====================================================

TeamRole = Literal["manager", "staff"]

GenderType = Literal["Male", "Female"]


# =====================================================
# Base Schema
# =====================================================

class TeamBase(BaseModel):
    name: str = Field(..., min_length=2)

    role: TeamRole

    gender: Optional[GenderType] = None

    email: Optional[EmailStr] = None

    contact: str

    emergency_contact: Optional[str] = None

    address: Optional[str] = None


    @field_validator("contact", "emergency_contact")
    @classmethod
    def validate_contact(cls, v: Optional[str]) -> Optional[str]:

        if v is None:
            return v

        cleaned = v.replace(" ", "").replace("+", "")

        if not cleaned.isdigit():
            raise ValueError("Contact must contain only numbers")

        if len(cleaned) < 7 or len(cleaned) > 15:
            raise ValueError("Contact must be between 7 and 15 digits")

        return cleaned


# =====================================================
# Create
# =====================================================

class TeamCreate(TeamBase):
    pass


# =====================================================
# Update
# =====================================================

class TeamUpdate(BaseModel):

    name: Optional[str] = Field(None, min_length=2)

    role: Optional[TeamRole] = None

    gender: Optional[GenderType] = None

    email: Optional[EmailStr] = None

    contact: Optional[str] = None

    emergency_contact: Optional[str] = None

    address: Optional[str] = None


# =====================================================
# Public Response
# =====================================================

class TeamResponse(BaseModel):

    id: UUID

    name: str

    role: TeamRole

    gender: Optional[GenderType]

    email: Optional[EmailStr]

    contact: str

    emergency_contact: Optional[str]

    address: Optional[str]

    created_at: Optional[datetime]

    updated_at: Optional[datetime]

    class Config:
        from_attributes = True