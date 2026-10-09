from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole
from models.user_model import User

from schema.user import UserCreate

from utils.password import hash_password


def get_business_member(
    db: Session,
    business_id,
    user_id,
) -> BusinessMember | None:

    return (
        db.query(BusinessMember)
        .filter(
            BusinessMember.business_id == business_id,
            BusinessMember.user_id == user_id,
        )
        .first()
    )


def get_business_members(
    db: Session,
    business_id,
):
    return (
        db.query(BusinessMember)
        .filter(
            BusinessMember.business_id == business_id
        )
        .all()
    )


def create_operator(
    db: Session,
    business: Business,
    user_data: UserCreate,
) -> BusinessMember:
    """
    Create a new user for an existing business.

    The new user is automatically assigned OPERATOR.
    """

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    if user_data.contact_number:

        existing_contact = (
            db.query(User)
            .filter(
                User.contact_number == user_data.contact_number
            )
            .first()
        )

        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this contact number already exists",
            )

    try:

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            contact_number=user_data.contact_number,
            avatar=user_data.avatar,
        )

        db.add(user)
        db.flush()

        member = BusinessMember(
            business_id=business.id,
            user_id=user.id,
            role=MemberRole.OPERATOR,
        )

        db.add(member)

        db.commit()
        db.refresh(member)

        return member

    except Exception:
        db.rollback()
        raise


def update_member_role(
    db: Session,
    member: BusinessMember,
    role: MemberRole,
) -> BusinessMember:

    if role == MemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner role cannot be assigned through this operation",
        )

    member.role = role

    db.commit()
    db.refresh(member)

    return member


def remove_member(
    db: Session,
    member: BusinessMember,
) -> None:

    if member.role == MemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business owner cannot be removed",
        )

    db.delete(member)
    db.commit()