from sqlalchemy import Integer, TIMESTAMP, ForeignKey, Index, Text
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
    from .product import Product


class Sale(Base):
    __tablename__ = "sales"

    __table_args__ = (
        Index("ix_sales_user_id", "user_id"),
        Index("ix_sales_product_id", "product_id"),
    )

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    product_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    profit_loss: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    contact: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="sales", lazy="selectin")
    product: Mapped["Product"] = relationship(back_populates="sales", lazy="selectin")
