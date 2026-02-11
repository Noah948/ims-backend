from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Any, Optional
from decimal import Decimal

class ProductCreate(BaseModel):
    category_id: UUID
    price: Decimal
    name: str
    stock: int
    minimum_stock: int
    dynamic_fields: dict[str, Any] | None = None

class ProductUpdate(BaseModel):
    price: Optional[Decimal] = None
    name: Optional[str] = None
    stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    dynamic_fields: dict[str, Any] | None = None

class ProductResponse(BaseModel):
    id: UUID
    category_id: UUID
    price: Decimal
    name: str
    stock: int
    minimum_stock: int
    dynamic_fields: dict | None
    created_at: datetime
# ✅ NEW — for add/remove quantity
class QuantityUpdate(BaseModel):
    quantity: int    

    class Config:
        from_attributes = True
