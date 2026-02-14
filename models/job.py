from sqlalchemy import Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from uuid import UUID as PyUUID
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

# Forward references for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    business_name: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    location: Mapped[Optional[str]] = mapped_column(Text)
    salary: Mapped[Optional[str]] = mapped_column(Text)
    email: Mapped[Optional[str]] = mapped_column(Text)
    contact: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    user: Mapped["User"] = relationship(back_populates="jobs", lazy="selectin")
