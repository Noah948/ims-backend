from sqlalchemy import Column, Integer, Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
from sqlalchemy.sql import func

class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)

    profit_loss = Column(Numeric(12, 2), nullable=False)

    contact = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
