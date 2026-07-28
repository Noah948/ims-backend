from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import (
    Boolean,
    Date,
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


class Expense(Base):
    __tablename__ = "expenses"

    __table_args__ = (
        Index("ix_expenses_business_id", "business_id"),
        Index("ix_expenses_expense_date", "expense_date"),
        Index(
            "ix_expenses_business_date",
            "business_id",
            "expense_date",
        ),
        Index("ix_expenses_deleted_at", "deleted_at"),
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

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    business: Mapped["Business"] = relationship(
        back_populates="expenses",
        lazy="selectin",
    )