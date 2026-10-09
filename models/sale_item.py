from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Numeric

from core.database import Base

if TYPE_CHECKING:
    from .sale import Sale
    from .product import Product


class SaleItem(Base):
    __tablename__ = "sale_items"

    __table_args__ = (
        Index("ix_sale_items_sale_id", "sale_id"),
        Index("ix_sale_items_product_id", "product_id"),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Parent Sale
    sale_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Product sold
    product_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    returned_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    is_fully_returned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    # Selling price per unit at the time of sale
    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Cost price per unit at the time of sale
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Profit/Loss for this line item
    profit_loss: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    sale: Mapped["Sale"] = relationship(
        back_populates="items",
        lazy="selectin",
    )

    product: Mapped["Product"] = relationship(
        back_populates="sale_items",
        lazy="selectin",
    )