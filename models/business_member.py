from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import (
    TIMESTAMP,
    ForeignKey,
    Index,
    Enum,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base
from models.enums import MemberRole

if TYPE_CHECKING:
    from .business import Business
    from .user import User


class BusinessMember(Base):
    __tablename__ = "business_members"

    __table_args__ = (
        Index("ix_business_member_business", "business_id"),
        Index("ix_business_member_user", "user_id"),
        Index("ix_business_member_role", "role"),
        Index("ix_business_member_business_role", "business_id", "role"),
        Index(
            "uq_business_member_business_user",
            "business_id",
            "user_id",
            unique=True,
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

    invited_by: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, name="member_role_enum"),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships

    business: Mapped["Business"] = relationship(
        back_populates="members",
    )

    user: Mapped["User"] = relationship(
        back_populates="business_memberships",
        foreign_keys=[user_id],
    )

    invited_by_user: Mapped["User"] = relationship(
        back_populates="invited_members",
        foreign_keys=[invited_by],
    )