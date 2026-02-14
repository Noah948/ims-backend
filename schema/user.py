from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


# =====================================================
# Base Shared Schema
# =====================================================

class UserBase(BaseModel):
    business_name: str = Field(..., min_length=2)
    business_type: str = Field(default="general", min_length=2)
    name: str = Field(..., min_length=2)
    contact_number: Optional[str] = None
    avatar: Optional[str] = None
    notifications_enabled: Optional[bool] = True


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
    business_type: Optional[str] = Field(None, min_length=2)
    name: Optional[str] = Field(None, min_length=2)
    contact_number: Optional[str] = None
    avatar: Optional[str] = None
    notifications_enabled: Optional[bool] = None


# =====================================================
# Public Response
# =====================================================

class UserResponse(BaseModel):
    id: UUID

    business_name: str
    business_type: str
    name: str
    email: EmailStr

    contact_number: Optional[str]
    avatar: Optional[str]
    notifications_enabled: bool

    # Subscription
    subscription_start_date: Optional[datetime]
    subscription_end_date: Optional[datetime]

    # Dashboard Counters
    total_products: int
    out_of_stock_count: int
    low_stock_count: int

    # Activity
    last_active_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Internal Schema (Optional – For Admin / Service Layer)
# =====================================================

class UserInternal(UserResponse):
    deleted_at: Optional[datetime]
