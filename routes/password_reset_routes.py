from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from schema.password_reset import (
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest
)
from services.password_reset_service import (
    request_password_reset,
    verify_otp,
    reset_password
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------- REQUEST OTP ----------------
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    result = request_password_reset(db, data.email)

    return {"message": "OTP sent to email"}


# ---------------- VERIFY OTP ----------------
@router.post("/verify-otp")
def verify_otp_endpoint(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):

    valid = verify_otp(db, data.email, data.otp)

    if not valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    return {"message": "OTP verified"}


# ---------------- RESET PASSWORD ----------------
@router.post("/reset-password")
def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    success = reset_password(
        db,
        data.email,
        data.otp,
        data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or email"
        )

    return {"message": "Password reset successful"}