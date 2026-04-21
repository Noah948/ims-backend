# services/otp_service.py

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import bcrypt
import secrets

from models.otp_model import OTP
from utils.otp_generator import generate_otp
from utils.email_service import send_otp_email

MAX_OTP_FAILURES = 5
OTP_EXPIRY_MINUTES = 10


def create_and_send_otp(db: Session, email: str, purpose: str):
    otp = generate_otp()
    otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()

    record = OTP(
        email=email,
        otp_hash=otp_hash,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )

    send_otp_email(email, otp, purpose)

    db.add(record)
    db.commit()

    return True


def verify_otp(db: Session, email: str, otp: str, purpose: str):
    now = datetime.utcnow()

    record = (
        db.query(OTP)
        .filter(
            OTP.email == email,
            OTP.purpose == purpose,
            OTP.is_used == False,
            OTP.is_deleted == False,
            OTP.expires_at > now
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not record:
        return None

    if bcrypt.checkpw(otp.encode(), record.otp_hash.encode()):

        token = secrets.token_urlsafe(32)

        record.token = token
        record.failed_attempts = 0

        db.commit()

        return token

    else:
        record.failed_attempts += 1

        if record.failed_attempts >= MAX_OTP_FAILURES:
            record.is_used = True

        db.commit()
        return None


def consume_token(db: Session, email: str, token: str, purpose: str):
    now = datetime.utcnow()

    record = (
        db.query(OTP)
        .filter(
            OTP.email == email,
            OTP.token == token,
            OTP.purpose == purpose,
            OTP.is_used == False,
            OTP.is_deleted == False,
            OTP.expires_at > now
        )
        .first()
    )

    if not record:
        return None

    record.is_used = True
    record.is_deleted = True

    db.commit()

    return True