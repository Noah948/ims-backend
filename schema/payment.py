from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal


# =====================================================
# Enums
# =====================================================

SubscriptionPlan = Literal["free", "starter", "pro"]

PaymentStatus = Literal[
    "pending",
    "active",
    "cancelled",
    "expired",
    "failed"
]


# =====================================================
# Provider Subscription Creation Response
# =====================================================

class SubscriptionCreateResponse(BaseModel):
    provider_subscription_id: str
    short_url: str


# =====================================================
# Internal Create Schema (Used After Webhook / Success)
# =====================================================

class PaymentCreate(BaseModel):
    provider_subscription_id: str
    provider_payment_id: Optional[str] = None
    subscription_plan: SubscriptionPlan
    status: PaymentStatus
    current_period_end: Optional[datetime] = None


# =====================================================
# Public Response
# =====================================================

class PaymentResponse(BaseModel):
    id: UUID
    subscription_plan: SubscriptionPlan
    status: PaymentStatus
    current_period_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
