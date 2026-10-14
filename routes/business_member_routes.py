from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_business, require_permission
from core.permissions import Permission

from models.business import Business
from models.business_member import BusinessMember

from schema.user import UserCreate
from schema.business_member import (
    BusinessMemberResponse,
    BusinessMemberUpdate,
)

from services.business_member_service import (
    create_operator,
    get_business_members,
    update_member_role,
    remove_member,
)


router = APIRouter(
    prefix="/business-members",
    tags=["Business Members"],
)


def get_member_or_404(
    db: Session,
    business_id,
    member_id: str,
) -> BusinessMember:

    member = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.id == member_id,
            BusinessMember.business_id == business_id,
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business member not found",
        )

    return member


@router.post(
    "/operators",
    response_model=BusinessMemberResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.INVITE_TEAM_MEMBERS))],
)
def create_business_operator(
    data: UserCreate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return create_operator(
        db=db,
        business=business,
        user_data=data,
    )


@router.get(
    "/",
    response_model=list[BusinessMemberResponse],
    dependencies=[Depends(require_permission(Permission.VIEW_TEAM_MEMBERS))],
)
def list_members(
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_business_members(
        db=db,
        business_id=business.id,
    )


@router.patch(
    "/{member_id}",
    response_model=BusinessMemberResponse,
    dependencies=[Depends(require_permission(Permission.CHANGE_USER_ROLES))],
)
def update_member(
    member_id: str,
    data: BusinessMemberUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    member = get_member_or_404(db, business.id, member_id)

    if data.role is None:
        return member

    return update_member_role(
        db=db,
        member=member,
        role=data.role,
    )


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.REMOVE_TEAM_MEMBERS))],
)
def delete_member(
    member_id: str,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    member = get_member_or_404(db, business.id, member_id)

    remove_member(
        db=db,
        member=member,
    )

    return None
