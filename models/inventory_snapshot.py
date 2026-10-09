from datetime import date, datetime
from decimal import Decimal
from uuid import UUID as PyUUID

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    TIMESTAMP,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import Numeric

from core.database import Base


# Daily per-business inventory state, written by scheduler/jobs/snapshot.py.
# Stock values can't be reconstructed later, so this is what powers the
# inventory value trend on the dashboard.
class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    __table_args__ = (
        UniqueConstraint(
            "business_id",
            "snapshot_date",
            name="uq_inventory_snapshots_business_date",
        ),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    business_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )

    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)

    total_units: Mapped[int] = mapped_column(Integer, nullable=False)

    stock_value: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    low_stock: Mapped[int] = mapped_column(Integer, nullable=False)

    out_of_stock: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )
