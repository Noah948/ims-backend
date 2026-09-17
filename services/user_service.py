import json
import os
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.redis import redis_client
from models.user_model import User
from schema.user import UserCreate, UserUpdate
from utils.email_service import send_verification_email
from utils.password import hash_password


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

REGISTRATION_PREFIX = "registration:"
REGISTRATION_TTL = 15 * 60  # 15 minutes


def _registration_key(registration_id: str) -> str:
    return f"{REGISTRATION_PREFIX}{registration_id}"


# =====================================================
# Register User
# =====================================================

def register_user(
    db: Session,
    data: UserCreate,
) -> dict:
    """
    Start registration.

    Checks PostgreSQL for existing email/contact first.
    If the user does not exist, registration data is temporarily
    stored in Redis and a verification email is sent.

    No database record is created during this step.
    """

    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    # -------------------------------------------------
    # Check existing user
    # -------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            (User.email == data.email)
            | (User.contact_number == data.contact_number)
        )
        .first()
    )

    if existing_user:

        if existing_user.email == data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact number already registered",
        )

    # -------------------------------------------------
    # Hash password
    # -------------------------------------------------

    password_hash = hash_password(data.password)

    # -------------------------------------------------
    # Create temporary registration ID
    # -------------------------------------------------

    registration_id = secrets.token_urlsafe(32)

    registration_data = {
        "full_name": data.full_name,
        "email": str(data.email),
        "password_hash": password_hash,
        "contact_number": data.contact_number,
        "avatar": data.avatar,
        "verified": False,
    }

    redis_key = _registration_key(registration_id)

    # -------------------------------------------------
    # Store registration in Redis
    # -------------------------------------------------

    redis_client.set(
        redis_key,
        json.dumps(registration_data),
        ex=REGISTRATION_TTL,
    )

    # -------------------------------------------------
    # Create verification JWT
    # -------------------------------------------------

    verification_payload = {
        "registration_id": registration_id,
        "email": str(data.email),

        # Important:
        # Identifies this JWT specifically as an
        # email verification token.
        "type": "email_verification",

        "exp": datetime.utcnow() + timedelta(minutes=15),
    }

    verification_token = jwt.encode(
        verification_payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    # -------------------------------------------------
    # Send verification email
    # -------------------------------------------------

    try:

        send_verification_email(
            email=str(data.email),
            token=verification_token,
        )

    except Exception:

        # If email sending fails, remove the temporary
        # registration from Redis.
        redis_client.delete(redis_key)

        raise

    return {
        "message": "Verification email sent successfully",
    }


# =====================================================
# Verify Email Token
# =====================================================

def verify_email_token(token: str) -> dict:
    """
    Verify the email verification token.

    This does NOT create anything in PostgreSQL.

    It only marks the temporary registration as verified
    in Redis.
    """

    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    # -------------------------------------------------
    # Decode JWT
    # -------------------------------------------------

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    # -------------------------------------------------
    # Validate token type
    # -------------------------------------------------

    if payload.get("type") != "email_verification":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    # -------------------------------------------------
    # Get registration ID
    # -------------------------------------------------

    registration_id = payload.get("registration_id")

    if not registration_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    # -------------------------------------------------
    # Get registration from Redis
    # -------------------------------------------------

    redis_key = _registration_key(registration_id)

    raw_registration = redis_client.get(redis_key)

    if not raw_registration:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration expired or does not exist",
        )

    # -------------------------------------------------
    # Decode registration data
    # -------------------------------------------------

    try:

        registration = json.loads(raw_registration)

    except (TypeError, json.JSONDecodeError):

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid registration data",
        )

    # -------------------------------------------------
    # Already verified
    # -------------------------------------------------

    if registration.get("verified"):

        return {
            "message": "Email already verified",
            "registration_id": registration_id,
        }

    # -------------------------------------------------
    # Mark as verified
    # -------------------------------------------------

    registration["verified"] = True

    redis_client.set(
        redis_key,
        json.dumps(registration),
        ex=REGISTRATION_TTL,
    )

    return {
        "message": "Email verified successfully",
        "registration_id": registration_id,
    }


# =====================================================
# Get Verified Registration
# =====================================================

def get_verified_registration(
    registration_id: str,
) -> dict:
    """
    Get verified registration data from Redis.
    """

    redis_key = _registration_key(registration_id)

    raw_registration = redis_client.get(redis_key)

    if not raw_registration:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration expired or does not exist",
        )

    try:

        registration = json.loads(raw_registration)

    except (TypeError, json.JSONDecodeError):

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid registration data",
        )

    if not registration.get("verified"):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email has not been verified",
        )

    return registration


# =====================================================
# Delete Registration
# =====================================================

def delete_registration(
    registration_id: str,
) -> None:

    redis_client.delete(
        _registration_key(registration_id)
    )


# =====================================================
# Get User By Email
# =====================================================

def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


# =====================================================
# Get User By ID
# =====================================================

def get_user_by_id(
    db: Session,
    user_id,
) -> User | None:

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


# =====================================================
# Update User
# =====================================================

def update_user(
    db: Session,
    user: User,
    data: UserUpdate,
) -> User:

    if data.full_name is not None:

        user.full_name = data.full_name

    if data.contact_number is not None:

        existing_contact = (
            db.query(User)
            .filter(
                User.contact_number == data.contact_number,
                User.id != user.id,
            )
            .first()
        )

        if existing_contact:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact number already exists",
            )

        user.contact_number = data.contact_number

    if data.avatar is not None:

        user.avatar = data.avatar

    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return user