from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2)
    contact_number: Optional[str] = Field(None, pattern=r"^[0-9]{10}$")
    avatar: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2)
    contact_number: Optional[str] = Field(None, pattern=r"^[0-9]{10}$")
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    contact_number: Optional[str]
    avatar: Optional[str]
    is_active: bool
    has_completed_onboarding: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInternal(UserResponse):
    deleted_at: Optional[datetime]



class VerifyPasswordChangeOTP(BaseModel):
    otp: str

class ChangePasswordRequest(BaseModel):
    change_token: str
    new_password: str