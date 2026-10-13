from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_business, get_current_membership

from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole

from schema.dashboard import DashboardRange, DashboardResponse
from services.dashboard_service import get_dashboard


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/",
    response_model=DashboardResponse,
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
        is_owner=membership.role == MemberRole.OWNER,
    )
