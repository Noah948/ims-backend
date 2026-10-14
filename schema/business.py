from pydantic import BaseModel, Field, computed_field
from uuid import UUID
from datetime import datetime
from typing import Optional
from models.enums import MemberRole, SubscriptionPlan, SubscriptionStatus
from core.permissions import Permission, ROLE_PERMISSIONS


class BusinessBase(BaseModel):
    name: str = Field(..., min_length=2)
    location: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    location: Optional[str] = None


class BusinessResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    location: Optional[str]
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus
    subscription_start: Optional[datetime]
    subscription_end: Optional[datetime]
    total_products: int
    low_stock_products: int
    out_of_stock_products: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Business of the current user, plus their role in it
class BusinessMeResponse(BusinessResponse):
    role: MemberRole

    # Lets the frontend hide actions the user can't perform.
    @computed_field
    @property
    def permissions(self) -> list[Permission]:
        return sorted(ROLE_PERMISSIONS.get(self.role, ()))
