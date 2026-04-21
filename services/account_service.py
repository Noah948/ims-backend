# services/account_service.py

import datetime

from sqlalchemy.orm import Session
from models.user_model import User
from services.otp_service import create_and_send_otp, verify_otp, consume_token

PURPOSE = "ACCOUNT_DELETE"


def request_account_deletion(db: Session, email: str):
    return create_and_send_otp(db, email, PURPOSE)


def verify_delete_otp(db: Session, email: str, otp: str):
    return verify_otp(db, email, otp, PURPOSE)


def delete_account(db: Session, email: str, token: str):

    valid = consume_token(db, email, token, PURPOSE)

    if not valid:
        return False

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False

    # SOFT DELETE
    user.deleted_at = datetime.datetime.utcnow()

    db.commit()

    return True