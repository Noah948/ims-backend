# services/user_service.py

from sqlalchemy.orm import Session
from uuid import UUID

from models.user_model import User, UserCreate
from utils.password import hash_password


def create_user(db: Session, data: UserCreate) -> User:
    """
    Create a new user (used internally or by admin).
    """
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role="owner",          # default role
        is_active=True,
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
