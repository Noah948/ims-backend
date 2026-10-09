from sqlalchemy.orm import Session

from models.user_model import User
from utils.password import hash_password

from services.otp_service import (
    create_and_send_otp,
    verify_otp,
    consume_token,
)


PURPOSE = "PASSWORD_RESET"


def request_password_reset(email: str):
    """
    Generate and send a password-reset OTP.
    OTP data is stored temporarily in Redis.
    """
    return create_and_send_otp(
        email=email,
        purpose=PURPOSE,
    )


def verify_reset_otp(
    email: str,
    otp: str,
):
    """
    Verify the password-reset OTP.

    Returns a short-lived reset token when successful.
    """
    return verify_otp(
        email=email,
        otp=otp,
        purpose=PURPOSE,
    )


def reset_password(
    db: Session,
    email: str,
    token: str,
    new_password: str,
):
    """
    Consume the reset token and update the user's password.
    """

    valid = consume_token(
        email=email,
        token=token,
        purpose=PURPOSE,
    )

    if not valid:
        return False

    user = (
        db.query(User)
        .filter(
            User.email == email,
            User.deleted_at.is_(None),
        )
        .first()
    )

    if not user:
        return False

    user.password_hash = hash_password(new_password)

    db.commit()

    return True