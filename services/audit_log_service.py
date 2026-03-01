from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional

from models.audit_log import AuditLog
from utils.pagination import paginate


def get_audit_logs(
    db: Session,
    user_id: UUID,
    page: int = 1,
    limit: int = 20,
    entity_type: Optional[str] = None,
    operation: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):

    query = select(AuditLog).where(AuditLog.user_id == user_id)

    # 🔎 Filters
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)

    if operation:
        query = query.where(AuditLog.operation == operation)

    if date_from:
        query = query.where(AuditLog.created_at >= date_from)

    if date_to:
        query = query.where(AuditLog.created_at <= date_to)

    query = query.order_by(AuditLog.created_at.desc())

    return paginate(query, db, page, limit)