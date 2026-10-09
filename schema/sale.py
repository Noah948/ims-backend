from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List


# =====================================================
# Sale Item Create
# =====================================================

class SaleItemCreate(BaseModel):
    product_id: UUID

    quantity: int = Field(..., gt=0)

    selling_price: Decimal = Field(..., gt=0)


# =====================================================
# Create Sale
# =====================================================

class SaleCreate(BaseModel):
    customer_contact: str

    items: List[SaleItemCreate]

    @field_validator("customer_contact")
    @classmethod
    def validate_customer_contact(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("+", "")

        if not cleaned.isdigit():
            raise ValueError("Contact must contain only numbers")

        if len(cleaned) != 10:
            raise ValueError("Contact must be exactly 10 digits")

        return cleaned


# =====================================================
# Sale Item Response
# =====================================================

class SaleItemResponse(BaseModel):
    id: UUID

    product_id: UUID

    quantity: int

    returned_quantity: int

    is_fully_returned: bool

    selling_price: Decimal

    cost_price: Decimal

    profit_loss: Decimal

    class Config:
        from_attributes = True


# =====================================================
# Sale Response
# =====================================================

class SaleResponse(BaseModel):
    id: UUID

    customer_contact: str

    total_amount: Decimal

    total_profit: Decimal

    created_at: datetime

    items: List[SaleItemResponse]

    class Config:
        from_attributes = True


# =====================================================
# Return Sale Item
# =====================================================

class SaleItemReturn(BaseModel):
    quantity: int = Field(..., gt=0)