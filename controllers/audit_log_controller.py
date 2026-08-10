from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional

from services.audit_log_service import get_audit_logs as get_audit_logs_service


def get_audit_logs(
    db: Session,
    business_id: UUID,
    page: int = 1,
    limit: int = 20,
    entity_type: Optional[str] = None,
    operation: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    return get_audit_logs_service(
        db=db,
        business_id=business_id,
        page=page,
        limit=limit,
        entity_type=entity_type,
        operation=operation,
        date_from=date_from,
        date_to=date_to,
    )