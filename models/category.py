from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from .business import Business
    from .product import Product


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    business_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    fields: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
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

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP,
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    business: Mapped["Business"] = relationship(
        back_populates="categories",
        lazy="selectin",
    )

    products: Mapped[List["Product"]] = relationship(
        back_populates="category",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------------------
    # Field Helpers
    # ------------------------------------------------------------------

    def ensure_fields(self) -> None:
        """Ensure fields is always initialized as a list."""
        if self.fields is None:
            self.fields = []

    def get_field(self, field_id: str) -> Optional[Dict[str, Any]]:
        """Return a field by its ID."""
        if not self.fields:
            return None

        return next(
            (field for field in self.fields if field.get("id") == field_id),
            None,
        )