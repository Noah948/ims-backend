from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user_model import User
from utils.password import verify_password
from utils.jwt import create_access_token


def authenticate_user(db: Session, email: str, password: str) -> dict:
    """
    Authenticate user and return JWT token.
    """

    user = db.query(User).filter(
        User.email == email,
        User.deleted_at.is_(None)
    ).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
