from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole
from models.user_model import User

from schema.business import BusinessCreate

from services.user_service import (
    get_verified_registration,
    delete_registration,
)


def complete_registration(
    db: Session,
    registration_id: str,
    business_data: BusinessCreate,
):
    """
    Complete the registration process.

    Creates all three records in one database transaction:

        User
        Business
        BusinessMember (OWNER)

    If anything fails, the entire transaction is rolled back.
    """

    registration = get_verified_registration(
        registration_id
    )

    email = registration["email"]

    # --------------------------------------------------
    # Safety checks before creating anything
    # --------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    contact_number = registration.get("contact_number")

    if contact_number:

        existing_contact = (
            db.query(User)
            .filter(
                User.contact_number == contact_number
            )
            .first()
        )

        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this contact number already exists",
            )

    # --------------------------------------------------
    # ONE DATABASE TRANSACTION
    # --------------------------------------------------

    try:

        # 1. Create User
        user = User(
            full_name=registration["full_name"],
            email=email,
            password_hash=registration["password_hash"],
            contact_number=contact_number,
            avatar=registration.get("avatar"),
        )

        db.add(user)
        db.flush()

        # 2. Create Business
        business = Business(
            owner_id=user.id,
            name=business_data.name,
            location=business_data.location,
        )

        db.add(business)
        db.flush()

        # 3. Create BusinessMember as OWNER
        member = BusinessMember(
            business_id=business.id,
            user_id=user.id,
            role=MemberRole.OWNER,
        )

        db.add(member)

        # Everything succeeds together.
        db.commit()

        db.refresh(user)
        db.refresh(business)
        db.refresh(member)

    except Exception:
        db.rollback()
        raise

    # Only delete temporary registration data AFTER
    # the database transaction succeeds.
    delete_registration(registration_id)

    return user, business, member


def get_business_by_id(
    db: Session,
    business_id,
) -> Business | None:

    return (
        db.query(Business)
        .filter(
            Business.id == business_id,
            Business.deleted_at.is_(None),
        )
        .first()
    )