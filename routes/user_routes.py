from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from models.user_model import User

from schema.password_reset import VerifyOTPRequest
from schema.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    VerifyPasswordChangeOTP,
    ChangePasswordRequest,
)


from services.user_service import (
    register_user,
    verify_email_token,
    update_user,
)

from services.deletion_service import (
    request_account_deletion,
    verify_delete_otp,
    delete_account,
)

from services.password_change_service import (
    request_password_change,
    verify_password_change_otp,
    change_password,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/register",
    status_code=status.HTTP_200_OK,
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(
        db=db,
        data=data,
    )


@router.get(
    "/verify-email",
    status_code=status.HTTP_200_OK,
)
def verify_email(
    token: str,
):
    return verify_email_token(token)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user(
        db=db,
        user=current_user,
        data=data,
    )


# =====================================================
# ACCOUNT DELETION
# =====================================================

@router.post("/request-delete")
def request_delete(
    current_user: User = Depends(get_current_user),
):
    request_account_deletion(current_user.email)

    return {
        "message": "OTP sent to your mail"
    }


@router.post("/verify-delete-otp")
def verify_delete(
    data: VerifyOTPRequest,
    current_user: User = Depends(get_current_user),
):
    token = verify_delete_otp(
        email=current_user.email,
        otp=data.otp,
    )

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    return {
        "message": "OTP verified successfully",
        "delete_token": token
    }


@router.post("/delete")
def delete(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_account(
        db=db,
        user=current_user,
        token=token,
    )


# password change

@router.post("/request-password-change")
def request_password_change_endpoint(
    current_user: User = Depends(get_current_user),
):
    request_password_change(current_user.email)

    return {
        "message": "Password change OTP sent to your email"
    }

@router.post("/verify-password-change-otp")
def verify_password_change_otp_endpoint(
    data: VerifyPasswordChangeOTP,
    current_user: User = Depends(get_current_user),
):
    token = verify_password_change_otp(
        email=current_user.email,
        otp=data.otp,
    )

    if not token:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP",
        )

    return {
        "message": "OTP verified",
        "change_token": token,
    }

@router.post("/change-password")
def change_password_endpoint(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = change_password(
        db=db,
        user=current_user,
        token=data.change_token,
        new_password=data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired change token",
        )

    return {
        "message": "Password changed successfully"
    }
