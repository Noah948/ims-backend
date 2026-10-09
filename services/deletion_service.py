from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user_model import User
from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole

from services.otp_service import (
    create_and_send_otp,
    verify_otp,
    consume_token,
)


PURPOSE = "ACCOUNT_DELETE"


def request_account_deletion(email: str):
    """
    Send an OTP to confirm account deletion.
    """

    return create_and_send_otp(
        email,
        PURPOSE,
    )


def verify_delete_otp(
    email: str,
    otp: str,
):
    """
    Verify the deletion OTP.

    The OTP service is responsible for generating the
    short-lived deletion token.
    """

    return verify_otp(
        email,
        otp,
        PURPOSE,
    )


def delete_account(
    db: Session,
    user: User,
    token: str,
):
    """
    Permanently initiate account deletion.

    OWNER:
        User is soft-deleted.
        Business is soft-deleted.

    OPERATOR:
        User is soft-deleted.
        BusinessMember is soft-deleted/removed.
        Business remains untouched.

    The actual permanent deletion happens later through
    the scheduled cleanup process.
    """

    valid = consume_token(
        user.email,
        token,
        PURPOSE,
    )

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired deletion token",
        )

    membership = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.user_id == user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business membership not found",
        )

    try:

        # ==============================================
        # OWNER
        # ==============================================

        if membership.role == MemberRole.OWNER:

            business = (
                db.query(Business)
                .filter(
                    Business.id == membership.business_id,
                    Business.deleted_at.is_(None),
                )
                .first()
            )

            if business:
                business.deleted_at = datetime.utcnow()

            user.deleted_at = datetime.utcnow()

        # ==============================================
        # OPERATOR
        # ==============================================

        elif membership.role == MemberRole.OPERATOR:

            user.deleted_at = datetime.utcnow()

            # Your current BusinessMember model does not
            # have deleted_at, so remove the membership.
            db.delete(membership)

        # ==============================================
        # UNKNOWN ROLE
        # ==============================================

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported member role",
            )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Account deletion initiated successfully",
    }