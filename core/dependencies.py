from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from core.database import get_db
from utils.jwt import decode_access_token
from models.user_model import User
from models.business import Business
from models.business_member import BusinessMember
from core.permissions import Permission, has_permission
from services.subscription_service import should_block_access

security = HTTPBearer()


@dataclass
class AuthContext:
    user: User
    membership: BusinessMember
    business: Business


def get_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AuthContext:
    # One round trip for user + membership + business. FastAPI caches this
    # per request, so every dependency below shares the same result.
    payload = decode_access_token(credentials.credentials)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    row = db.execute(
        select(User, BusinessMember, Business)
        .outerjoin(BusinessMember, BusinessMember.user_id == User.id)
        .outerjoin(Business, and_(
            Business.id == BusinessMember.business_id,
            Business.deleted_at.is_(None),
        ))
        .where(User.id == payload["sub"], User.deleted_at.is_(None))
    ).first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    user, membership, business = row

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No business associated with this account",
        )

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

    return AuthContext(user, membership, business)


def get_current_user(ctx: AuthContext = Depends(get_auth_context)) -> User:
    return ctx.user


def get_current_business(ctx: AuthContext = Depends(get_auth_context)) -> Business:
    return ctx.business


def get_current_membership(ctx: AuthContext = Depends(get_auth_context)) -> BusinessMember:
    return ctx.membership


def require_permission(*permissions: Permission):
    """Route guard: `dependencies=[Depends(require_permission(Permission.X))]`.
    All listed permissions are required. Returns the AuthContext, so it can
    also be used as a regular parameter dependency."""
    def checker(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        missing = [p for p in permissions if not has_permission(ctx.membership.role, p)]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action",
            )
        return ctx
    return checker
