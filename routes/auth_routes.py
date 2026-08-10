from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from services.rate_limiter.dependency import rate_limit
from services.rate_limiter.policies import AuthRateLimits


from schema.user import UserResponse, UserLogin
from schema.password_reset import ForgotPasswordRequest, VerifyOTPRequest

from utils.auth import authenticate_user
from services.account_recovery_service import (
    request_account_recovery,
    recover_account,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


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


# frontend can handle the logout by simply deleting the token on the client side.
@router.post("/logout") 
def logout(): return { 
    "message": "Logged out successfully" 
    }


#  recover deleted account

@router.post("/recovery/request")
def recovery_request(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    request_account_recovery(db, data.email)

    return {
        "message": "If the account is eligible for recovery, an OTP has been sent to the registered email."
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