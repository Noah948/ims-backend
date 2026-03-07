from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional


# =====================================================
# Create Sale
# =====================================================

class SaleCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)

    contact: str

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("+", "")

        if not cleaned.isdigit():
            raise ValueError("Contact must contain only numbers")

        if len(cleaned) != 10:
            raise ValueError("Contact must be exactly 10 digits")

        return cleaned


# =====================================================
# Public Response
# =====================================================

class SaleResponse(BaseModel):
    id: UUID
    product_id: UUID

    quantity: int
    selling_price: Decimal
    profit_loss: Decimal

    contact: str
    created_at: datetime

    class Config:
        from_attributes = True