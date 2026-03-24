from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from models.password_reset_otp import PasswordResetOTP
from models.user_model import User
from utils.password import hash_password

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

    token = verify_otp(db, data.email, data.otp)

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    return {
        "message": "OTP verified",
        "reset_token": token
    }


# ---------------- RESET PASSWORD ----------------
@router.post("/reset-password")
def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    success = reset_password(
        db,
        data.email,
        data.new_password   # ✅ no OTP, no token
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="OTP not verified or expired"
        )

    return {"message": "Password reset successful"}
 