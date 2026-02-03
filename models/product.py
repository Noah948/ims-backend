from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.database import Base
import uuid
from sqlalchemy.sql import func
from sqlalchemy.types import Numeric

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)

    price= Column(Numeric(10,2), nullable=False)
    name = Column(Text, nullable=False)

    stock = Column(Integer, nullable=False)
    minimum_stock = Column(Integer, nullable=False)

    dynamic_fields = Column(JSONB)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())
