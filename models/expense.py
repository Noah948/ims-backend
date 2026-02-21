from sqlalchemy import Boolean, Date, TIMESTAMP, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric
from typing import Optional
from uuid import UUID as PyUUID
from datetime import datetime
from sqlalchemy.sql import func
from core.database import Base

# Forward references for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User


class Expense(Base):
    __tablename__ = "expenses"

    __table_args__ = (
        Index("ix_expenses_user_id", "user_id"),
        Index("ix_expenses_expense_date", "expense_date"),
        Index("ix_expenses_user_date", "user_id", "expense_date"),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(Text, nullable=False)

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),   # financial precision
        nullable=False
    )

    expense_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False
    )

    description: Mapped[Optional[str]] = mapped_column(Text)

    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Soft delete support
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    user: Mapped["User"] = relationship(
        back_populates="expenses",
        lazy="selectin"
    )