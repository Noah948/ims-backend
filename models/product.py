from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID as PyUUID

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Numeric

from core.database import Base

if TYPE_CHECKING:
    from .business import Business
    from .category import Category
    from .sale_item import SaleItem


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        Index("ix_products_business_id", "business_id"),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_deleted_at", "deleted_at"),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    business_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )

    category_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    minimum_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    dynamic_fields: Mapped[Optional[dict]] = mapped_column(
        JSONB,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    business: Mapped["Business"] = relationship(
        back_populates="products",
        lazy="selectin",
    )

    category: Mapped["Category"] = relationship(
        back_populates="products",
        lazy="selectin",
    )

    sale_items: Mapped[List["SaleItem"]] = relationship(
        back_populates="product",
        lazy="selectin",
    )