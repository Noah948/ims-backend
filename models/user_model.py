from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID as PyUUID

from sqlalchemy import (
    Boolean,
    Index,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from .business import Business
    from .business_member import BusinessMember
    from .sale import Sale
    from .job import Job
    from .audit_log import AuditLog


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_contact_number", "contact_number"),
        Index("ix_users_deleted_at", "deleted_at"),
    )

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # -------------------------------------------------------------------------
    # Authentication
    # -------------------------------------------------------------------------

    full_name: Mapped[str] = mapped_column(Text, nullable=False)

    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Profile
    # -------------------------------------------------------------------------

    contact_number: Mapped[Optional[str]] = mapped_column(
        Text,
        unique=True,
    )

    avatar: Mapped[Optional[str]] = mapped_column(Text)

    # -------------------------------------------------------------------------
    # Account
    # -------------------------------------------------------------------------

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    has_completed_onboarding: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------

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

    deleted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    # Businesses owned by this user
    owned_businesses: Mapped[List["Business"]] = relationship(
        back_populates="owner",
        lazy="selectin",
    )

    # Businesses where this user is a member
    business_memberships: Mapped[List["BusinessMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="BusinessMember.user_id",
    )

    # Members invited by this user
    invited_members: Mapped[List["BusinessMember"]] = relationship(
        back_populates="invited_by_user",
        lazy="selectin",
        foreign_keys="BusinessMember.invited_by",
    )

    # Sales created by this user
    sales: Mapped[List["Sale"]] = relationship(
        back_populates="created_by_user",
        lazy="selectin",
    )

    # Jobs created by this user
    jobs: Mapped[List["Job"]] = relationship(
        back_populates="created_by_user",
        lazy="selectin",
    )

    # Audit logs performed by this user
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )