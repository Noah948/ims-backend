from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    Index,
    Text,
    CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from uuid import UUID as PyUUID, uuid4
from datetime import datetime
from decimal import Decimal

from sqlalchemy.sql import func

from core.database import Base

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .user_model import User
    from .sale_item import SaleItem


class Sale(Base):
    __tablename__ = "sales"

    __table_args__ = (
        Index("ix_sales_user_id", "user_id"),

        CheckConstraint(
            "contact ~ '^[0-9]{10}$'",
            name="ck_sales_contact_10_digits"
        ),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # customer contact
    contact: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # overall bill amount
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    # total profit from all items
    total_profit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    # relationships
    user: Mapped["User"] = relationship(
        back_populates="sales",
        lazy="selectin"
    )

    items: Mapped[List["SaleItem"]] = relationship(
        back_populates="sale",
        lazy="selectin",
        cascade="all, delete-orphan"
    )