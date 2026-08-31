from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from services.rate_limiter.dependency import rate_limit
from services.rate_limiter.policies import AuthRateLimits

from services.user_service import (
    register_user,
    verify_email_token,
)

from services.auth_service import (
    request_account_recovery,
    recover_account,
)

from utils.auth import authenticate_user

from schema.user import (
    UserCreate,
    UserLogin,
    UserResponse,
)

from schema.password_reset import (
    ForgotPasswordRequest,
    VerifyOTPRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

# @router.post("/register")
# def register(
#     data: UserCreate,
#     db: Session = Depends(get_db),
# ):
#     return register_user(
#         db=db,
#         data=data,
#     )


# ------------------------------------------------------------------
# Email Verification
# ------------------------------------------------------------------

# @router.get("/verify-email")
# def verify_email(
#     token: str,
#     db: Session = Depends(get_db),
# ):
#     return verify_email_token(
#         db=db,
#         token=token,
#     )


# ------------------------------------------------------------------
# Login
# ------------------------------------------------------------------

@router.post(
    "/login",
    dependencies=[
        Depends(rate_limit(AuthRateLimits.LOGIN))
    ],
)
def login(
    request: Request,
    data: UserLogin,
    db: Session = Depends(get_db),
):
    return authenticate_user(
        db=db,
        email=data.email,
        password=data.password,
    )


# ------------------------------------------------------------------
# Logout
# ------------------------------------------------------------------

@router.post("/logout")
def logout():
    # JWT is stateless, so the client removes its token.
    return {
        "message": "Logged out successfully"
    }


# ------------------------------------------------------------------
# Current User
# ------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user=Depends(get_current_user),
):
    return current_user


# ------------------------------------------------------------------
# Account Recovery
# ------------------------------------------------------------------

@router.post("/recovery/request")
def recovery_request(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    request_account_recovery(
        db=db,
        email=data.email,
    )

    return {
        "message": (
            "If the account is eligible for recovery, "
            "an OTP has been sent to the registered email."
        )
    }


@router.post("/recovery/verify-otp")
def recovery_verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db),
):
    return recover_account(
        db=db,
        email=data.email,
        otp=data.otp,
    )