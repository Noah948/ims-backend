from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class ExpenseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)
    expense_date: date
    is_recurring: bool = False


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    expense_date: Optional[date] = None
    is_recurring: Optional[bool] = None


class ExpenseResponse(ExpenseBase):
    id: UUID
    business_id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DateFilter(BaseModel):
    from_date: Optional[date] = Field(None, alias="from")
    to_date: Optional[date] = Field(None, alias="to")


class AmountFilter(BaseModel):
    min: Optional[Decimal] = None
    max: Optional[Decimal] = None


class ExpenseFilter(BaseModel):
    date: Optional[DateFilter] = None
    amount: Optional[AmountFilter] = None
    is_recurring: Optional[bool] = None
    search: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)