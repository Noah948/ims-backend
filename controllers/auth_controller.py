from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from services.auth_service import register_user, verify_email_token
from utils.auth import authenticate_user
from models.user_model import User
from schema.user import UserCreate, UserLogin


def register(db: Session, data: UserCreate):
    return register_user(db, data)


def verify_email(db: Session, token: str):
    return verify_email_token(db, token)


def login(db: Session, data: UserLogin):
    return authenticate_user(
        db=db,
        email=data.email,
        password=data.password
    )


def me(user: User):
    return user