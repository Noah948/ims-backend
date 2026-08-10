from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.database import get_db
from utils.jwt import decode_access_token
from models.user_model import User
from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(
        User.id == payload["sub"],
        User.deleted_at.is_(None)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def get_current_business(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Business:
    membership = (
        db.query(BusinessMember)
        .filter(BusinessMember.user_id == user.id)
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No business found for current user"
        )

    business = db.query(Business).filter(
        Business.id == membership.business_id,
        Business.deleted_at.is_(None)
    ).first()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    return business


def require_role(required_role: MemberRole):
    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        membership = (
            db.query(BusinessMember)
            .filter(
                BusinessMember.user_id == user.id,
                BusinessMember.role == required_role
            )
            .first()
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return checker