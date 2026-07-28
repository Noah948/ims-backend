from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    Index,
    Text,
    Enum,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base
from models.enums import SubscriptionPlan


if TYPE_CHECKING:
    from .business import Business


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        Index("ix_payments_business_id", "business_id"),
        Index("ix_payments_status", "status"),
        Index("ix_payments_provider_payment_id", "provider_payment_id"),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Business subscription owner
    business_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Payment gateway subscription id
    provider_subscription_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Payment gateway transaction id
    provider_payment_id: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(
            SubscriptionPlan,
            name="subscription_plan_enum",
        ),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "PENDING",
            "ACTIVE",
            "CANCELLED",
            "EXPIRED",
            "FAILED",
            name="payment_status_enum",
        ),
        nullable=False,
    )

    current_period_end: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
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

    # ------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------

    business: Mapped["Business"] = relationship(
        back_populates="payments",
        lazy="selectin",
    )