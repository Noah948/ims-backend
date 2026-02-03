from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PaymentCreate(BaseModel):
    transaction_id: str
    payment_date: datetime

class PaymentResponse(BaseModel):
    id: UUID
    transaction_id: str
    payment_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
