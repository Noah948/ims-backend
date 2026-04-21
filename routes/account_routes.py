from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.password_reset import VerifyOTPRequest

from services.account_service import (
    request_account_deletion,
    verify_delete_otp,
    delete_account
)

router = APIRouter(prefix="/account", tags=["Account"])


# 🔐 STEP 1: Request OTP
@router.post("/request-delete")
def request_delete(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request_account_deletion(db, current_user.email)
    return {"message": "OTP sent to your email"}


# 🔐 STEP 2: Verify OTP
@router.post("/verify-delete-otp")
def verify_delete(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    token = verify_delete_otp(db, current_user.email, data.otp)

    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    return {"delete_token": token}


# 🔐 STEP 3: Delete Account
@router.post("/delete")
def delete(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    success = delete_account(db, current_user.email, token)

    if not success:
        raise HTTPException(status_code=400, detail="Invalid token")

    return {"message": "Account deleted successfully"}