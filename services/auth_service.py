from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

from models.user_model import User
from schema.user import UserCreate

from utils.password import hash_password

from utils.email_service import (
    send_verification_email
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


# =========================================================
# UPDATED REGISTER USER
# NOW WORKS AS SIGNUP FLOW
# =========================================================

def register_user(
    db: Session,
    data: UserCreate
):
    """
    Register user with email verification.
    User is only saved after verification.
    """

    # Check duplicate email/contact
    existing_user = db.query(User).filter(
        (User.email == data.email) |
        (User.contact_number == data.contact_number)
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with same email or contact already exists",
        )

    # Hash password
    hashed_password = hash_password(
        data.password
    )

    # JWT payload
    payload = {
        "user_name": data.user_name,
        "business_name": data.business_name,
        "email": data.email,
        "password_hash": hashed_password,
        "contact_number": data.contact_number,
        "avatar": data.avatar,
        "location": data.location,
        "exp": (
            datetime.utcnow() +
            timedelta(minutes=15)
        )
    }

    # Generate verification token
    verification_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # Send verification email
    send_verification_email(
        email=data.email,
        token=verification_token
    )

    return {
        "message": (
            "Verification email sent successfully"
        )
    }


# =========================================================
# VERIFY EMAIL
# =========================================================

def verify_email_token(
    db: Session,
    token: str
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Prevent reuse
    existing_user = db.query(User).filter(
        User.email == payload["email"]
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link already used"
        )

    # Create actual user
    user = User(
        user_name=payload["user_name"],
        business_name=payload["business_name"],
        email=payload["email"],
        password_hash=payload["password_hash"],
        contact_number=payload["contact_number"],
        avatar=payload["avatar"],
        location=payload["location"]
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": (
            "Email verified successfully"
        )
    }