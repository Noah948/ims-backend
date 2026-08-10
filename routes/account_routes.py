# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from core.database import get_db
# from core.dependencies import get_current_user
# from models.user_model import User
# from schema.password_reset import VerifyOTPRequest

# from services.account_service import request_delete, verify_delete, delete

# router = APIRouter(prefix="/account", tags=["Account"])


# @router.post("/request-delete")
# def request_delete_endpoint(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     return request_delete(current_user.email)


# @router.post("/verify-delete-otp")
# def verify_delete_endpoint(
#     data: VerifyOTPRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     return verify_delete(db, current_user.email, data.otp)


# @router.post("/delete")
# def delete_endpoint(
#     token: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     return delete(db, current_user.email, token)