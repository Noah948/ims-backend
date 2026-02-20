from sqlalchemy import Integer, TIMESTAMP, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric
from typing import Optional, List
from uuid import UUID as PyUUID, uuid4
from datetime import datetime
from sqlalchemy.sql import func
from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User
    from .category import Category
    from .sale import Sale


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        Index("ix_products_user_id", "user_id"),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_deleted_at", "deleted_at"),
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

    # 🔥 CHANGED TO CASCADE
    category_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    minimum_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    dynamic_fields: Mapped[Optional[dict]] = mapped_column(
        JSONB
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        onupdate=func.now()
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP
    )

    user: Mapped["User"] = relationship(
        back_populates="products",
        lazy="selectin"
    )

    category: Mapped["Category"] = relationship(
        back_populates="products",
        lazy="selectin"
    )

    sales: Mapped[List["Sale"]] = relationship(
        back_populates="product",
        lazy="selectin"
    )
