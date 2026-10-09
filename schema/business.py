from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from models.enums import SubscriptionPlan, SubscriptionStatus


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