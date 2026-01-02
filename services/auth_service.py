# services/auth_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user_model import User
from utils.password import hash_password, verify_password
from utils.jwt import create_access_token


def register_user(db: Session, email: str, password: str):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=email,
        password_hash=hash_password(password),
        role="owner",
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return {"access_token": token, "token_type": "bearer"}
