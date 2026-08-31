
from datetime import datetime, timedelta
import os

from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from models.user_model import User
from models.business import Business
from models.business_member import BusinessMember
from models.enums import (
    MemberRole,
    SubscriptionPlan,
    SubscriptionStatus,
)

from schema.user import UserCreate

from services.otp_service import (
    create_and_send_otp,
    verify_otp,
)

from utils.password import hash_password
from utils.email_service import send_verification_email


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


# ================================================================
# EMAIL VERIFICATION
# ================================================================

EMAIL_VERIFICATION_EXPIRY_MINUTES = 15


# def register_user(db: Session, data: UserCreate):
#     existing_user = db.query(User).filter(
#         (User.email == data.email) |
#         (User.contact_number == data.contact_number)
#     ).first()

#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User with same email or contact already exists",
#         )

#     hashed_password = hash_password(data.password)

#     payload = {
#         "full_name": data.full_name,
#         "email": data.email,
#         "password_hash": hashed_password,
#         "contact_number": data.contact_number,
#         "avatar": data.avatar,
#         "exp": (
#             datetime.utcnow()
#             + timedelta(minutes=EMAIL_VERIFICATION_EXPIRY_MINUTES)
#         ),
#     }

#     verification_token = jwt.encode(
#         payload,
#         SECRET_KEY,
#         algorithm=ALGORITHM,
#     )

#     send_verification_email(
#         email=data.email,
#         token=verification_token,
#     )

#     return {
#         "message": "Verification email sent successfully"
#     }


# def verify_email_token(db: Session, token: str):
#     try:
#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM],
#         )
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired token",
#         )

#     existing_user = (
#         db.query(User)
#         .filter(User.email == payload["email"])
#         .first()
#     )

#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Verification link already used",
#         )

#     user = User(
#         full_name=payload["full_name"],
#         email=payload["email"],
#         password_hash=payload["password_hash"],
#         contact_number=payload.get("contact_number"),
#         avatar=payload.get("avatar"),
#     )

#     db.add(user)
#     db.flush()

#     business = Business(
#         owner_id=user.id,
#         name=f"{payload['full_name']}'s Business",
#     )

#     db.add(business)
#     db.flush()

#     member = BusinessMember(
#         business_id=business.id,
#         user_id=user.id,
#         role=MemberRole.OWNER,
#     )

#     db.add(member)

#     db.commit()
#     db.refresh(user)

#     return {
#         "message": "Email verified successfully"
#     }


# ================================================================
# ACCOUNT RECOVERY
# ================================================================

RECOVERY_PURPOSE = "ACCOUNT_RECOVERY"

RECOVERY_PERIOD_DAYS = 90

# Temporary development assumption:
# successful OTP verification = successful payment
RECOVERY_PLAN = SubscriptionPlan.BASIC
RECOVERY_SUBSCRIPTION_DAYS = 30


def request_account_recovery(
    db: Session,
    email: str,
):
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
            detail=(
                "Account recovery is not available "
                "because this account is active."
            ),
        )

    recovery_deadline = (
        user.deleted_at
        + timedelta(days=RECOVERY_PERIOD_DAYS)
    )

    if datetime.utcnow() > recovery_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account recovery period has expired.",
        )

    return create_and_send_otp(
        email=email,
        purpose=RECOVERY_PURPOSE,
    )


def recover_account(
    db: Session,
    email: str,
    otp: str,
):
    """
    Verify recovery OTP and restore the deleted owner account.

    Temporary behavior:
    successful OTP verification is treated as
    successful payment.
    """

    # ------------------------------------------------------------
    # Find deleted user
    # ------------------------------------------------------------

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

    # ------------------------------------------------------------
    # Check recovery window
    # ------------------------------------------------------------

    recovery_deadline = (
        user.deleted_at
        + timedelta(days=RECOVERY_PERIOD_DAYS)
    )

    if datetime.utcnow() > recovery_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recovery period has expired",
        )

    # ------------------------------------------------------------
    # Find owner's deleted business
    # ------------------------------------------------------------

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

    # ------------------------------------------------------------
    # Verify OTP
    # ------------------------------------------------------------

    token = verify_otp(
        email=email,
        otp=otp,
        purpose=RECOVERY_PURPOSE,
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # ------------------------------------------------------------
    # Temporary payment assumption
    # ------------------------------------------------------------

    now = datetime.utcnow()

    # ------------------------------------------------------------
    # Restore user
    # ------------------------------------------------------------

    user.deleted_at = None

    # ------------------------------------------------------------
    # Restore business
    # ------------------------------------------------------------

    business.deleted_at = None

    # ------------------------------------------------------------
    # Restore owner's membership
    # ------------------------------------------------------------

    membership = (
        db.query(BusinessMember)
        .filter(
            BusinessMember.business_id == business.id,
            BusinessMember.user_id == user.id,
            BusinessMember.role == MemberRole.OWNER,
        )
        .first()
    )

    if membership and hasattr(membership, "deleted_at"):
        membership.deleted_at = None

    # ------------------------------------------------------------
    # Activate subscription
    # ------------------------------------------------------------

    business.subscription_plan = RECOVERY_PLAN
    business.subscription_status = SubscriptionStatus.ACTIVE
    business.subscription_start = now
    business.subscription_end = (
        now
        + timedelta(days=RECOVERY_SUBSCRIPTION_DAYS)
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
