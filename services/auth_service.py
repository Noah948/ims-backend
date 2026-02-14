
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user_model import User
from schema.user import UserCreate
from utils.password import hash_password


def register_user(db: Session, data: UserCreate) -> User:
    """
    Register a new user.
    """

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        name=data.name,
        business_name=data.business_name,
        business_type=data.business_type,
        email=data.email,
        password_hash=hash_password(data.password),
        contact_number=data.contact_number,
        notifications_enabled=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
