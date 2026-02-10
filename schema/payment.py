from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class SubscriptionCreateResponse(BaseModel):
    subscription_id: str
    short_url: str


class PaymentResponse(BaseModel):
    id: UUID
    subscription_id: str
    status: str
    current_period_end: Optional[datetime]

    class Config:
        from_attributes = True
