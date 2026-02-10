from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base
import uuid
from datetime import datetime

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    subscription_id = Column(Text, nullable=False)
    payment_id = Column(Text, nullable=True)

    status = Column(Text, nullable=False)  # active, cancelled, expired
    current_period_end = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
