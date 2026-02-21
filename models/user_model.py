from sqlalchemy import (
    Text, Boolean, Integer, TIMESTAMP, text, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List, Optional
from uuid import UUID as PyUUID
from datetime import datetime

from core.database import Base

# Forward references for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .team import Team
    from .product import Product
    from .sale import Sale
    from .payment import Payment
    from .job import Job
    from .category import Category
    from .audit_log import AuditLog
    from .expense import Expense


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_deleted_at", "deleted_at"),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    business_name: Mapped[str] = mapped_column(Text, nullable=False)
    business_type: Mapped[str] = mapped_column(Text, nullable=False, server_default="general")
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    contact_number: Mapped[Optional[str]] = mapped_column(Text)
    avatar: Mapped[Optional[str]] = mapped_column(Text)

    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False
    )

    subscription_start_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    subscription_end_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    total_products: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    out_of_stock_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    low_stock_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    last_active_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    # Relationships
    teams: Mapped[List["Team"]] = relationship(back_populates="user", lazy="selectin")
    products: Mapped[List["Product"]] = relationship(back_populates="user", lazy="selectin")
    sales: Mapped[List["Sale"]] = relationship(back_populates="user", lazy="selectin")
    payments: Mapped[List["Payment"]] = relationship(back_populates="user", lazy="selectin")
    jobs: Mapped[List["Job"]] = relationship(back_populates="user", lazy="selectin")
    categories: Mapped[List["Category"]] = relationship(back_populates="user", lazy="selectin")
    audit_logs = relationship(
    "AuditLog",
    back_populates="user",
    cascade="all, delete",
    lazy="selectin"
    )
    expenses: Mapped[list["Expense"]] = relationship(
    back_populates="user",
    lazy="selectin",
    cascade="all, delete-orphan"
)

