from sqlalchemy import TIMESTAMP, Text, Boolean, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from core.database import Base


class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    email: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        index=True
    )

    otp: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    failed_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )