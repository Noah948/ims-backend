from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional


# =====================================================
# Create Sale (Immutable Record)
# =====================================================

class SaleCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)
    contact: Optional[str] = None

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        cleaned = v.replace(" ", "").replace("+", "")

        if not cleaned.isdigit():
            raise ValueError("Contact must contain only numbers")

        return v


# =====================================================
# Public Response
# =====================================================

class SaleResponse(BaseModel):
    id: UUID
    product_id: UUID

    quantity: int
    selling_price: Decimal
    profit_loss: Decimal

    contact: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
