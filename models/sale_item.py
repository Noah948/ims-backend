from sqlalchemy import (
    Integer,
    TIMESTAMP,
    ForeignKey,
    Index
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from uuid import UUID as PyUUID, uuid4
from datetime import datetime
from decimal import Decimal

from sqlalchemy.sql import func

from core.database import Base

from typing import TYPE_CHECKING

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
        default=uuid4
    )

    # parent sale / invoice
    sale_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False
    )

    # sold product
    product_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    returned_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    is_fully_returned: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )
    
    # selling price per unit
    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # original product cost price per unit
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # total profit/loss for this item
    profit_loss: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    # relationships
    sale: Mapped["Sale"] = relationship(
        back_populates="items",
        lazy="selectin"
    )

    product: Mapped["Product"] = relationship(
        back_populates="sale_items",
        lazy="selectin"
    )