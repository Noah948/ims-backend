from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user_model import User
from schema.user import UserCreate
from utils.password import hash_password


def register_user(db: Session, data: UserCreate) -> User:
    """
    Register a new user.
    """

    # Check duplicate email or contact
    existing_user = db.query(User).filter(
        (User.email == data.email) |
        (User.contact_number == data.contact_number)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with same email or contact already exists",
        )

    user = User(
        user_name=data.user_name,
        business_name=data.business_name,
        email=data.email,
        password_hash=hash_password(data.password),
        contact_number=data.contact_number,
        avatar=data.avatar
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user