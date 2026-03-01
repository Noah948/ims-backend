from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.common import PaginatedResponse
from schema.audit_log import AuditLogResponse
from services.audit_log_service import get_audit_logs

from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "/",
    response_model=PaginatedResponse[AuditLogResponse]
)
def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),

    entity_type: Optional[str] = None,
    operation: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_audit_logs(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        entity_type=entity_type,
        operation=operation,
        date_from=date_from,
        date_to=date_to,
    )