# routes/auth_routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.auth_service import register_user, authenticate_user
from core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    return register_user(db, email, password)


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    return authenticate_user(db, email, password)


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }
