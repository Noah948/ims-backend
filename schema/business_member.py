from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from models.enums import MemberRole


class BusinessMemberBase(BaseModel):
    user_id: UUID
    role: MemberRole


class BusinessMemberCreate(BaseModel):
    user_id: UUID
    role: MemberRole = MemberRole.OPERATOR


class BusinessMemberUpdate(BaseModel):
    role: Optional[MemberRole] = None


class MemberUserInfo(BaseModel):
    full_name: str
    email: str
    contact_number: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class BusinessMemberResponse(BaseModel):
    id: UUID
    business_id: UUID
    user_id: UUID
    invited_by: Optional[UUID]
    role: MemberRole
    joined_at: datetime
    created_at: datetime
    updated_at: datetime
    user: Optional[MemberUserInfo] = None

    class Config:
        from_attributes = True