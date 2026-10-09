from sqlalchemy.orm import Session

from models.user_model import User
from utils.password import hash_password
from services.otp_service import (
    create_and_send_otp,
    verify_otp,
    consume_token,
)

PURPOSE = "PASSWORD_CHANGE"


def request_password_change(email: str):
    return create_and_send_otp(
        email=email,
        purpose=PURPOSE,
    )


def verify_password_change_otp(email: str, otp: str):
    return verify_otp(
        email=email,
        otp=otp,
        purpose=PURPOSE,
    )


def change_password(
    db: Session,
    user: User,
    token: str,
    new_password: str,
):
    valid = consume_token(
        email=user.email,
        token=token,
        purpose=PURPOSE,
    )

    if not valid:
        return False

    user.password_hash = hash_password(new_password)

    db.commit()

    return True