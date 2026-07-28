from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID as PyUUID

from sqlalchemy import (
    Index,
    Integer,
    Text,
    TIMESTAMP,
    ForeignKey,
    text,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base
from models.enums import SubscriptionPlan, SubscriptionStatus

if TYPE_CHECKING:
    from .user import User
    from .business_member import BusinessMember
    from .category import Category
    from .product import Product
    from .sale import Sale
    from .expense import Expense
    from .payment import Payment
    from .job import Job
    from .audit_log import AuditLog


class Business(Base):
    __tablename__ = "businesses"

    __table_args__ = (
        Index("ix_business_owner", "owner_id"),
        Index("ix_business_deleted_at", "deleted_at"),
        Index("ix_business_subscription_status", "subscription_status"),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    owner_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)

    location: Mapped[Optional[str]] = mapped_column(Text)

    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan, name="subscription_plan_enum"),
        nullable=False,
        server_default="TRIAL",
    )

    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status_enum"),
        nullable=False,
        server_default="TRIAL",
    )

    subscription_start: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    subscription_end: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    total_products: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    low_stock_products: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    out_of_stock_products: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    # Relationships

    owner: Mapped["User"] = relationship(
        back_populates="owned_businesses",
    )

    members: Mapped[List["BusinessMember"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    categories: Mapped[List["Category"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    products: Mapped[List["Product"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    sales: Mapped[List["Sale"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    payments: Mapped[List["Payment"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    jobs: Mapped[List["Job"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        lazy="selectin",
    )