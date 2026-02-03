from sqlalchemy import Column, Text, Boolean, Integer, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")  # DB generates UUID
    )

    business_name = Column(Text, nullable=False)
    business_type = Column(Text, nullable=False, server_default="general")
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    contact_number = Column(Text)
    avatar = Column(Text)
    notifications_enabled = Column(Boolean, server_default=text("true"))

    subscription_start_date = Column(TIMESTAMP)
    subscription_end_date = Column(TIMESTAMP)

    total_products = Column(Integer, default=0, server_default="0")
    out_of_stock_count = Column(Integer, default=0, server_default="0")
    low_stock_count = Column(Integer, default=0, server_default="0")


    last_active_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP)
