from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

from models.user_model import User
from models.business import Business
from models.business_member import BusinessMember
from models.enums import MemberRole
from schema.user import UserCreate

from utils.password import hash_password
from utils.email_service import send_verification_email

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def register_user(db: Session, data: UserCreate):
    existing_user = db.query(User).filter(
        (User.email == data.email) |
        (User.contact_number == data.contact_number)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with same email or contact already exists",
        )

    hashed_password = hash_password(data.password)

    payload = {
        "full_name": data.full_name,
        "email": data.email,
        "password_hash": hashed_password,
        "contact_number": data.contact_number,
        "avatar": data.avatar,
        "exp": (datetime.utcnow() + timedelta(minutes=15))
    }

    verification_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    send_verification_email(email=data.email, token=verification_token)

    return {"message": "Verification email sent successfully"}


def verify_email_token(db: Session, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    existing_user = db.query(User).filter(User.email == payload["email"]).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link already used"
        )

    user = User(
        full_name=payload["full_name"],
        email=payload["email"],
        password_hash=payload["password_hash"],
        contact_number=payload.get("contact_number"),
        avatar=payload.get("avatar"),
    )
    db.add(user)
    db.flush()

    business = Business(
        owner_id=user.id,
        name=f"{payload['full_name']}'s Business",
    )
    db.add(business)
    db.flush()

    member = BusinessMember(
        business_id=business.id,
        user_id=user.id,
        role=MemberRole.OWNER,
    )
    db.add(member)
    db.commit()
    db.refresh(user)

    return {"message": "Email verified successfully"}