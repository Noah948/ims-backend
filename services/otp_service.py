from datetime import datetime, timedelta
import bcrypt
import secrets

from core.redis import redis_client
from utils.email_service import send_otp_email

MAX_OTP_FAILURES = 5
OTP_EXPIRY_MINUTES = 10

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def _otp_key(email: str, purpose: str) -> str:
    return f"otp:{purpose}:{email}"


def create_and_send_otp(email: str, purpose: str):
    otp = generate_otp()
    otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()

    data = {
        "otp_hash": otp_hash,
        "failed_attempts": "0",
        "is_used": "false",
        "token": "",
    }

    key = _otp_key(email, purpose)

    redis_client.hset(key, values=data)

    redis_client.expire(_otp_key(email, purpose), OTP_EXPIRY_MINUTES * 60)

    send_otp_email(email, otp, purpose)

    return True


def verify_otp(email: str, otp: str, purpose: str):
    key = _otp_key(email, purpose)
    record = redis_client.hgetall(key)

    if not record:
        return None

    stored_hash = record.get("otp_hash", "")
    if not stored_hash:
        return None

    if record.get("is_used") == "true":
        return None

    if bcrypt.checkpw(otp.encode(), stored_hash.encode()):
        token = secrets.token_urlsafe(32)
        redis_client.hset(key, "token", token)
        redis_client.hset(key, "failed_attempts", "0")
        return token

    failed = int(record.get("failed_attempts", "0")) + 1
    redis_client.hset(key, "failed_attempts", str(failed))

    if failed >= MAX_OTP_FAILURES:
        redis_client.hset(key, "is_used", "true")

    return None


def consume_token(email: str, token: str, purpose: str):
    key = _otp_key(email, purpose)
    record = redis_client.hgetall(key)

    if not record:
        return None

    if record.get("is_used") == "true":
        return None

    stored_token = record.get("token", "")
    if not stored_token or stored_token != token:
        return None

    redis_client.hset(key, "is_used", "true")
    redis_client.expire(key, 60)

    return True