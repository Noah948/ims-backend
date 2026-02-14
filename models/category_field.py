from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from core.database import Base

# Forward references for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .category import Category

class CategoryField(Base):
    __tablename__ = "category_fields"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)

    category_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    field_name: Mapped[str] = mapped_column(Text, nullable=False)
    field_type: Mapped[str] = mapped_column(Text, nullable=False)

    dropdown_options: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text)
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

    category: Mapped["Category"] = relationship(
        back_populates="fields",
        lazy="selectin"
    )
