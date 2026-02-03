from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


# --------------------
# Auth / Create
# --------------------
class UserCreate(BaseModel):
    business_name: str = Field(..., min_length=2)
    business_type: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    contact_number: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --------------------
# Update Profile
# --------------------
class UserUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    name: Optional[str] = None
    contact_number: Optional[str] = None
    avatar: Optional[str] = None
    notifications_enabled: Optional[bool] = None


# --------------------
# Public Response
# --------------------
class UserResponse(BaseModel):
    id: UUID

    business_name: str
    business_type: str
    name: str
    email: EmailStr

    contact_number: Optional[str]
    avatar: Optional[str]
    notifications_enabled: bool

    total_products: int
    out_of_stock_count: int
    low_stock_count: int

    last_active_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
