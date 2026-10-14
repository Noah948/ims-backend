from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import AuthContext, get_auth_context, require_permission
from core.permissions import Permission

from schema.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessMeResponse,
    BusinessUpdate,
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


@router.get(
    "/me",
    response_model=BusinessMeResponse,
)
def get_my_business(
    ctx: AuthContext = Depends(get_auth_context),
):
    return BusinessMeResponse(
        **BusinessResponse.model_validate(ctx.business).model_dump(),
        role=ctx.membership.role,
    )


@router.patch(
    "/me",
    response_model=BusinessMeResponse,
    dependencies=[Depends(require_permission(Permission.UPDATE_BUSINESS_SETTINGS))],
)
def update_my_business(
    data: BusinessUpdate,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    business = ctx.business

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(business, field, value)

    db.commit()
    db.refresh(business)

    return BusinessMeResponse(
        **BusinessResponse.model_validate(business).model_dump(),
        role=ctx.membership.role,
    )
