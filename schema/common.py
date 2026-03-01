from pydantic import BaseModel
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic.generics import GenericModel

T = TypeVar("T")


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(GenericModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta