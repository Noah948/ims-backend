from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db

from schema.password_reset import (
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
)

from services.password_reset_service import (
    request_password_reset,
    verify_reset_otp,
    reset_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
):
    request_password_reset(data.email)

    return {
        "message": "OTP sent to your email"
    }


@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPRequest,
):
    token = verify_reset_otp(
        email=data.email,
        otp=data.otp,
    )

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP",
        )

    return {
        "message": "OTP verified",
        "reset_token": token,
    }


@router.post("/reset-password")
def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    success = reset_password(
        db=db,
        email=data.email,
        token=data.reset_token,
        new_password=data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    return {
        "message": "Password reset successful"
    }