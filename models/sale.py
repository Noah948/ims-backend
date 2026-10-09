from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List
from uuid import UUID as PyUUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Numeric

from core.database import Base

if TYPE_CHECKING:
    from .business import Business
    from .user import User
    from .sale_item import SaleItem


class Sale(Base):
    __tablename__ = "sales"

    __table_args__ = (
        Index("ix_sales_business_id", "business_id"),
        Index("ix_sales_created_by", "created_by"),
        CheckConstraint(
            "customer_contact ~ '^[0-9]{10}$'",
            name="ck_sales_customer_contact_10_digits",
        ),
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

    created_by: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    customer_contact: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    total_profit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    business: Mapped["Business"] = relationship(
        back_populates="sales",
        lazy="selectin",
    )

    created_by_user: Mapped["User"] = relationship(
        back_populates="sales",
        lazy="selectin",
    )

    items: Mapped[List["SaleItem"]] = relationship(
        back_populates="sale",
        lazy="selectin",
        cascade="all, delete-orphan",
    )