from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(Text, nullable=False)
    gender = Column(Text)
    email = Column(Text)
    contact = Column(Text)
    emergency_contact = Column(Text)
    address = Column(Text)
    role = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
