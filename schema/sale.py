from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class SaleCreate(BaseModel):
    product_id: UUID
    quantity: int
    selling_price: Decimal
    contact: str | None = None

    @field_validator("contact")
    @classmethod
    def contact_must_be_numeric(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("Contact must contain only numbers")
        return v


class SaleResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    selling_price: Decimal
    profit_loss: Decimal
    contact: str | None
    created_at: datetime

    class Config:
        from_attributes = True
