from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from core.database import Base


class CategoryField(Base):
    __tablename__ = "category_fields"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)

    category_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),  # 🔥 Important
        nullable=False
    )

    field_name: Mapped[str] = mapped_column(Text, nullable=False)
    field_type: Mapped[str] = mapped_column(Text, nullable=False)
    dropdown_options: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    # 🔥 Relationship back to Category
    category = relationship("Category", back_populates="fields")
