from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from decimal import Decimal


# =====================================================
# Base Shared Schema
# =====================================================

class ProductBase(BaseModel):
    category_id: Optional[UUID] = None
    price: Decimal = Field(..., gt=0)
    name: str = Field(..., min_length=1)
    stock: int = Field(..., ge=0)
    minimum_stock: int = Field(..., ge=0)
    dynamic_fields: Optional[dict[str, Any]] = None


# =====================================================
# Create
# =====================================================

class ProductCreate(ProductBase):
    pass


# =====================================================
# Update
# =====================================================

class ProductUpdate(BaseModel):
    category_id: Optional[UUID] = None
    price: Optional[Decimal] = Field(None, gt=0)
    name: Optional[str] = Field(None, min_length=1)
    stock: Optional[int] = Field(None, ge=0)
    minimum_stock: Optional[int] = Field(None, ge=0)
    dynamic_fields: Optional[dict[str, Any]] = None


# =====================================================
# Quantity Update (Stock Adjustments)
# =====================================================

class QuantityUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


# =====================================================
# Public Response
# =====================================================

class ProductResponse(BaseModel):
    id: UUID
    category_id: Optional[UUID]

    price: Decimal
    name: str
    stock: int
    minimum_stock: int

    dynamic_fields: Optional[dict[str, Any]]

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
