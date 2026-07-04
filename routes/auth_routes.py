from services.rate_limiter.dependency import rate_limit
from services.rate_limiter.policies import AuthRateLimits
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from services.auth_service import (
    register_user,
    verify_email_token
)

from utils.auth import authenticate_user

from schema.user import (
    UserCreate,
    UserResponse,
    UserLogin
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# =====================================================
# REGISTER
# NOW SENDS VERIFICATION EMAIL
# =====================================================

@router.post("/register", dependencies=[Depends(rate_limit(AuthRateLimits.REGISTER))])
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(db, data)


# =====================================================
# VERIFY EMAIL
# =====================================================

@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    return verify_email_token(
        db=db,
        token=token
    )


# =====================================================
# LOGIN (JSON BASED)
# =====================================================

@router.post("/login", dependencies=[Depends(rate_limit(AuthRateLimits.LOGIN))])
def login(
    request: Request,
    data: UserLogin,
    db: Session = Depends(get_db),
):
    return authenticate_user(
        db=db,
        email=data.email,
        password=data.password
    )


# =====================================================
# CURRENT USER
# =====================================================

@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user