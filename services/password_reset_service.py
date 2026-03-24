from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import bcrypt
import secrets

from models.password_reset_otp import PasswordResetOTP
from models.user_model import User
from utils.otp_generator import generate_otp
from utils.email_service import send_password_reset_otp
from utils.password import hash_password

MAX_OTP_FAILURES = 5


# ---------------- REQUEST OTP ----------------
def request_password_reset(db: Session, email: str):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return True  # prevent user enumeration

    otp = generate_otp()
    otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()

    expires_at = datetime.utcnow() + timedelta(minutes=10)

    otp_record = PasswordResetOTP(
        email=email,
        otp_hash=otp_hash,
        expires_at=expires_at,
    )

    send_password_reset_otp(email, otp)

    db.add(otp_record)
    db.commit()

    return True


# ---------------- VERIFY OTP ----------------
def verify_otp(db: Session, email: str, otp: str):

    now = datetime.utcnow()

    record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.email == email,
            PasswordResetOTP.is_used == False,
            PasswordResetOTP.is_deleted == False,
            PasswordResetOTP.expires_at > now
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )

    if not record:
        return None

    if bcrypt.checkpw(otp.encode(), record.otp_hash.encode()):

        # 🔐 generate secure reset token
        reset_token = secrets.token_urlsafe(32)

        record.reset_token = reset_token
        record.failed_attempts = 0

        db.commit()

        return reset_token

    else:
        record.failed_attempts += 1

        if record.failed_attempts >= MAX_OTP_FAILURES:
            record.is_used = True

        db.commit()
        return None

# ---------------- RESET PASSWORD ----------------
def reset_password(db: Session, email: str, reset_token: str, new_password: str):

    now = datetime.utcnow()

    record = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.email == email,
            PasswordResetOTP.reset_token == reset_token,
            PasswordResetOTP.is_used == False,
            PasswordResetOTP.is_deleted == False,
            PasswordResetOTP.expires_at > now
        )
        .first()
    )

    if not record:
        return False

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False

    # 🔐 update password
    user.password_hash = hash_password(new_password)

    # ✅ mark OTP as consumed + soft delete
    record.is_used = True
    record.is_deleted = True

    db.commit()

    return True