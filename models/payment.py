from sqlalchemy import TIMESTAMP, ForeignKey, func, Enum, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID, uuid4
from datetime import datetime
from core.database import Base

# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        Index("ix_payments_user_id", "user_id"),
        Index("ix_payments_status", "status"),
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

    # External provider identifiers (Stripe/Razorpay/etc.)
    provider_subscription_id: Mapped[str] = mapped_column(Text, nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(Text)

    # Internal plan control
    subscription_plan: Mapped[str] = mapped_column(
        Enum("free", "starter", "pro", name="subscription_plan_enum"),
        nullable=False
    )

    # Subscription lifecycle
    status: Mapped[str] = mapped_column(
        Enum("pending", "active", "cancelled", "expired", "failed", name="payment_status_enum"),
        nullable=False
    )

    current_period_end: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="payments",
        lazy="selectin"
    )
