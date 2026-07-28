from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Text,
    TIMESTAMP,
    text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


if TYPE_CHECKING:
    from .business import Business
    from .user import User


class Job(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        Index("ix_jobs_business_id", "business_id"),
        Index("ix_jobs_created_by", "created_by"),
        CheckConstraint(
            "contact ~ '^[0-9]{10}$'",
            name="ck_jobs_contact_10_digits",
        ),
    )

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Business that owns this job posting
    business_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )

    # User who created the job
    created_by: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    location: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    salary: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    email: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    contact: Mapped[str] = mapped_column(
        Text,
        nullable=False,
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

    # ------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------

    business: Mapped["Business"] = relationship(
        back_populates="jobs",
        lazy="selectin",
    )

    created_by_user: Mapped["User"] = relationship(
        back_populates="jobs",
        lazy="selectin",
    )