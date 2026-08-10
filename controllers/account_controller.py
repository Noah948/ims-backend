from sqlalchemy.orm import Session

from services.account_service import (
    request_account_deletion,
    verify_delete_otp,
    delete_account,
)


def request_delete(email: str):
    request_account_deletion(email)
    return {"message": "OTP sent to your email"}


def verify_delete(db: Session, email: str, otp: str):
    token = verify_delete_otp(email, otp)
    if not token:
        raise_for_invalid_otp()
    return {"delete_token": token}


def delete(db: Session, email: str, token: str):
    success = delete_account(db, email, token)
    if not success:
        raise_for_invalid_token()
    return {"message": "Account deleted successfully"}


def raise_for_invalid_otp():
    from fastapi import HTTPException
    raise HTTPException(status_code=400, detail="Invalid or expired OTP")


def raise_for_invalid_token():
    from fastapi import HTTPException
    raise HTTPException(status_code=400, detail="Invalid token")