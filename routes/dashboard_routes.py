from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_business, get_current_user

from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole
from models.user_model import User

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
    user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
):
    role = (
        db.query(BusinessMember.role)
        .filter(
            BusinessMember.user_id == user.id,
            BusinessMember.business_id == business.id,
        )
        .scalar()
    )

    return get_dashboard(
        db,
        business,
        range,
        is_owner=role == MemberRole.OWNER,
    )
