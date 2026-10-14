from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_business, get_current_membership, require_permission
from core.permissions import Permission, has_permission

from models.business import Business
from models.business_member import BusinessMember

from schema.dashboard import DashboardRange, DashboardResponse
from services.dashboard_service import get_dashboard


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/",
    response_model=DashboardResponse,
    dependencies=[Depends(require_permission(Permission.VIEW_DASHBOARD))],
)
def get_dashboard_endpoint(
    range: DashboardRange = Query("month"),
    db: Session = Depends(get_db),
    membership: BusinessMember = Depends(get_current_membership),
    business: Business = Depends(get_current_business),
):
    return get_dashboard(
        db,
        business,
        range,
        is_owner=has_permission(membership.role, Permission.VIEW_FULL_REPORTS),
    )
