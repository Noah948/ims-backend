from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User
    from .product import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    fields: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        nullable=True,
        index=True
    )

    user: Mapped["User"] = relationship(
        back_populates="categories",
        lazy="selectin"
    )

    products: Mapped[List["Product"]] = relationship(
        back_populates="category",
        lazy="selectin"
    )

    # =========================
    # Field Helpers
    # =========================

    def ensure_fields(self) -> None:
        """Ensure fields is always initialized as a list"""
        if self.fields is None:
            self.fields = []

    def get_field(self, field_id: str) -> Optional[Dict[str, Any]]:
        """Safely retrieve a field by ID"""
        if not self.fields:
            return None

        return next(
            (f for f in self.fields if f.get("id") == field_id),
            None
        )