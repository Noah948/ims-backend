from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class SaleCreate(BaseModel):
    product_id: UUID
    quantity: int
    selling_price: Decimal
    contact: str | None = None

class SaleResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    selling_price: Decimal
    contact: str | None
    status: bool
    created_at: datetime

    class Config:
        from_attributes = True
