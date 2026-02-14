from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List
from uuid import UUID
from datetime import datetime
from core.database import Base

# Forward references for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User  
    from .product import Product
    from .category_field import CategoryField


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)

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

    products: Mapped[List["Product"]] = relationship(
        back_populates="category",
        lazy="selectin"
    )

    fields: Mapped[List["CategoryField"]] = relationship(
        back_populates="category",
        cascade="all, delete",
        passive_deletes=True,
        lazy="selectin"
    )
