from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from services.auth_service import register_user
from utils.auth import authenticate_user
from schema.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, data)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible login for Swagger.
    - username = email
    - password = password
    """
    return authenticate_user(
        db=db,
        email=form_data.username,  # Swagger uses "username"
        password=form_data.password
    )


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user
