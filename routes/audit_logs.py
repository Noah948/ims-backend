from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_business

from models.business import Business

from schema.common import PaginatedResponse
from schema.audit_log import AuditLogResponse

from services.audit_log_service import get_audit_logs


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


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
    business: Business = Depends(get_current_business),
):
    return get_audit_logs(
        db=db,
        business_id=business.id,
        page=page,
        limit=limit,
        entity_type=entity_type,
        operation=operation,
        date_from=date_from,
        date_to=date_to,
    )