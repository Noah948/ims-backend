from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db

from schema.business import (
    BusinessCreate,
    BusinessResponse,
)

from services.business_service import (
    complete_registration,
)


router = APIRouter(
    prefix="/businesses",
    tags=["Businesses"],
)


@router.post(
    "/onboard",
    status_code=status.HTTP_201_CREATED,
)
def complete_business_onboarding(
    registration_id: str,
    data: BusinessCreate,
    db: Session = Depends(get_db),
):
    user, business, member = complete_registration(
        db=db,
        registration_id=registration_id,
        business_data=data,
    )

    return {
        "message": "Registration completed successfully",
        "user_id": str(user.id),
        "business_id": str(business.id),
        "business_member_id": str(member.id),
    }