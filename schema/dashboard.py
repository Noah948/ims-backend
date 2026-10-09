from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel


DashboardRange = Literal["today", "7d", "month", "year"]


# Owner-only fields are Optional and come back as None for OPERATOR members.

class DashboardSummary(BaseModel):
    revenue: float
    orders: int
    avg_order_value: float
    units_sold: int
    return_rate: float  # % of sold units returned
    unique_customers: int
    repeat_customers: int
    gross_profit: Optional[float] = None
    margin: Optional[float] = None  # % of revenue
    expenses: Optional[float] = None
    net_profit: Optional[float] = None


class InventoryState(BaseModel):
    product_count: int
    total_units: int
    stock_value: float  # at cost (products.price)
    low_stock: int
    out_of_stock: int


class TrendPoint(BaseModel):
    label: str
    revenue: float
    profit: Optional[float] = None
    expenses: Optional[float] = None


class CategorySlice(BaseModel):
    name: str
    revenue: float


class TopProduct(BaseModel):
    name: str
    units: int
    revenue: float
    profit: Optional[float] = None


class HeatCell(BaseModel):
    dow: int  # 0 = Sunday
    hour: int
    orders: int


class RestockItem(BaseModel):
    name: str
    stock: int
    minimum_stock: int
    daily_rate: float  # avg units/day over last 30 days
    days_left: Optional[float] = None  # None when there were no recent sales


class DeadStockItem(BaseModel):
    name: str
    stock: int
    value: float
    last_sold: Optional[date] = None


class InventoryPoint(BaseModel):
    date: date
    stock_value: float
    total_units: int


class TeamMember(BaseModel):
    name: str
    orders: int
    revenue: float


class TopCustomer(BaseModel):
    contact: str  # masked
    orders: int
    revenue: float


class DashboardResponse(BaseModel):
    range: DashboardRange
    is_owner: bool
    summary: DashboardSummary
    inventory: InventoryState
    trend: List[TrendPoint]
    categories: List[CategorySlice]
    top_products: List[TopProduct]
    heatmap: List[HeatCell]
    restock: List[RestockItem]
    dead_stock: List[DeadStockItem]
    inventory_trend: List[InventoryPoint]
    team: List[TeamMember]
    top_customers: List[TopCustomer]
