from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional
import re


# =====================================================
# Base Shared Schema
# =====================================================

class UserBase(BaseModel):
    business_name: str = Field(..., min_length=2)
    user_name: str = Field(..., min_length=2)

    contact_number: Optional[str] = Field(
        None,
        pattern=r"^[0-9]{10}$"
    )

    avatar: Optional[str] = None


# =====================================================
# Create / Auth
# =====================================================

class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =====================================================
# Update Profile
# =====================================================

class UserUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2)
    user_name: Optional[str] = Field(None, min_length=2)

    contact_number: Optional[str] = Field(
        None,
        pattern=r"^[0-9]{10}$"
    )

    avatar: Optional[str] = None


# =====================================================
# Public Response
# =====================================================

class UserResponse(BaseModel):
    id: UUID

    business_name: str
    user_name: str
    email: EmailStr

    contact_number: Optional[str]
    avatar: Optional[str]

    subscription_start_date: Optional[datetime]
    subscription_end_date: Optional[datetime]

    total_products: int
    out_of_stock_count: int
    low_stock_count: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Internal Schema
# =====================================================

class UserInternal(UserResponse):
    deleted_at: Optional[datetime]