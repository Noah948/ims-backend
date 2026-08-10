from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole
from models.user_model import User

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


def get_owner_business(
    db: Session,
    current_user: User,
) -> Business:

    membership = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.user_id == current_user.id,
            BusinessMember.role == MemberRole.OWNER,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the business owner can perform this action",
        )

    business = (
        db.query(Business)
        .filter(
            Business.id == membership.business_id,
            Business.deleted_at.is_(None),
        )
        .first()
    )

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return business


@router.post(
    "/operators",
    response_model=BusinessMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_operator(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owner_business(
        db=db,
        current_user=current_user,
    )

    return create_operator(
        db=db,
        business=business,
        user_data=data,
    )


@router.get(
    "/",
    response_model=list[BusinessMemberResponse],
)
def list_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owner_business(
        db=db,
        current_user=current_user,
    )

    return get_business_members(
        db=db,
        business_id=business.id,
    )


@router.patch(
    "/{member_id}",
    response_model=BusinessMemberResponse,
)
def update_member(
    member_id: str,
    data: BusinessMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owner_business(
        db=db,
        current_user=current_user,
    )

    member = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.id == member_id,
            BusinessMember.business_id == business.id,
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business member not found",
        )

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
)
def delete_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_owner_business(
        db=db,
        current_user=current_user,
    )

    member = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.id == member_id,
            BusinessMember.business_id == business.id,
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business member not found",
        )

    remove_member(
        db=db,
        member=member,
    )

    return None