from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from services.auth_service import register_user
from utils.auth import authenticate_user
from schema.user import UserCreate, UserResponse, UserLogin

router = APIRouter(prefix="/auth", tags=["Auth"])


# ==============================
# REGISTER
# ==============================
@router.post("/register", response_model=UserResponse)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    return register_user(db, data)


# ==============================
# LOGIN (JSON BASED)
# ==============================
@router.post("/login")
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Accepts JSON:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    return authenticate_user(
        db=db,
        email=data.email,
        password=data.password
    )


# ==============================
# CURRENT USER
# ==============================
@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user