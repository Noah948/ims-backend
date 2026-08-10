from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user_model import User
from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole, SubscriptionPlan, SubscriptionStatus

from services.otp_service import (
    create_and_send_otp,
    verify_otp,
)


PURPOSE = "ACCOUNT_RECOVERY"

RECOVERY_PERIOD_DAYS = 90

# Temporary development assumption:
# successful OTP verification = successful payment
RECOVERY_PLAN = SubscriptionPlan.BASIC
RECOVERY_SUBSCRIPTION_DAYS = 30


def request_account_recovery(db: Session, email: str):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    if user.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account recovery is not available because this account is active.",
        )

    recovery_deadline = user.deleted_at + timedelta(
        days=RECOVERY_PERIOD_DAYS
    )

    if datetime.utcnow() > recovery_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account recovery period has expired.",
        )

    return create_and_send_otp(
        email=email,
        purpose=PURPOSE,
    )

def recover_account(
    db: Session,
    email: str,
    otp: str,
):
    """
    Verify recovery OTP and restore the deleted owner account.

    For now, successful OTP verification is treated as
    successful payment.
    """

    # -------------------------------------------------
    # Find deleted user
    # -------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.email == email,
            User.deleted_at.is_not(None),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is not available for recovery",
        )

    # -------------------------------------------------
    # Check 90-day recovery window
    # -------------------------------------------------

    recovery_deadline = user.deleted_at + timedelta(
        days=RECOVERY_PERIOD_DAYS
    )

    if datetime.utcnow() > recovery_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recovery period has expired",
        )

    # -------------------------------------------------
    # Find owner's deleted business
    # -------------------------------------------------

    business = (
        db.query(Business)
        .filter(
            Business.owner_id == user.id,
            Business.deleted_at.is_not(None),
        )
        .first()
    )

    if not business:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business is not available for recovery",
        )

    # -------------------------------------------------
    # Verify OTP
    # -------------------------------------------------

    token = verify_otp(
        email=email,
        otp=otp,
        purpose=PURPOSE,
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # -------------------------------------------------
    # TEMPORARY PAYMENT ASSUMPTION
    #
    # OTP verification currently means:
    # payment successful
    # -------------------------------------------------

    now = datetime.utcnow()

    # Restore user
    user.deleted_at = None

    # Restore business
    business.deleted_at = None

    # -------------------------------------------------
    # Restore owner's membership
    # -------------------------------------------------

    membership = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.business_id == business.id,
            BusinessMember.user_id == user.id,
            BusinessMember.role == MemberRole.OWNER,
        )
        .first()
    )

    if membership:
        # If your BusinessMember model has deleted_at,
        # restore it.
        if hasattr(membership, "deleted_at"):
            membership.deleted_at = None

    # -------------------------------------------------
    # Activate paid subscription
    # -------------------------------------------------

    business.subscription_plan = RECOVERY_PLAN
    business.subscription_status = SubscriptionStatus.ACTIVE
    business.subscription_start = now
    business.subscription_end = (
        now + timedelta(days=RECOVERY_SUBSCRIPTION_DAYS)
    )

    db.commit()

    db.refresh(user)
    db.refresh(business)

    return {
        "message": "Account recovered successfully",
        "subscription_plan": business.subscription_plan,
        "subscription_status": business.subscription_status,
        "subscription_end": business.subscription_end,
    }