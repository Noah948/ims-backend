from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from models.user_model import User
from models.business import Business
from models.business_member import BusinessMember

from utils.password import verify_password
from utils.jwt import create_access_token

from services.subscription_service import should_block_access

def authenticate_user(db: Session, email: str, password: str) -> dict:
    """
    Authenticate user and return JWT token.
    """

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user or not verify_password(password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    membership = db.query(BusinessMember).filter(
        BusinessMember.user_id == user.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No business associated with this account",
        )

    business = db.query(Business).filter(
        Business.id == membership.business_id,
        Business.deleted_at.is_(None),
    ).first()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Business is no longer available",
        )

    if should_block_access(business):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription expired. Please renew your subscription to continue.",
        )

    if user.deleted_at is not None:
        recovery_deadline = user.deleted_at + timedelta(days=90)

        if datetime.utcnow() <= recovery_deadline:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_DELETION_PENDING",
                    "message": "Your account is scheduled for deletion.",
                    "recovery_available": True,
                },
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been permanently deleted.",
        )

    token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
