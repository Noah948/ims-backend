from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

class CategoryField(Base):
    __tablename__ = "category_fields"

    id = Column(UUID(as_uuid=True), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    field_name = Column(Text, nullable=False)
    field_type = Column(Text, nullable=False)
    dropdown_options = Column(ARRAY(Text))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
