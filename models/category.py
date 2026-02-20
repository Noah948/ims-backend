from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List, Optional
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

    name: Mapped[str] = mapped_column(Text, nullable=False)

    fields: Mapped[Optional[List[dict]]] = mapped_column(
        JSONB,
        nullable=True
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

    user: Mapped["User"] = relationship(
        back_populates="categories",
        lazy="selectin"
    )

    # 🔥 CASCADE DELETE ENABLED
    products: Mapped[List["Product"]] = relationship(
        back_populates="category",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
