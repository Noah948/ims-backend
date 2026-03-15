import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

if not EMAIL_USER or not EMAIL_PASS:
    raise ValueError("EMAIL_USER and EMAIL_PASS environment variables must be set")


def send_password_reset_otp(email: str, otp: str):

    subject = "Password Reset OTP"
    body = f"""
Your password reset OTP is:

{otp}

This OTP will expire in 10 minutes.

If you did not request this, please ignore this email.
"""

    message = MIMEText(body)
    message["Subject"] = str(subject)
    message["From"] = str(EMAIL_USER)
    message["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(str(EMAIL_USER), str(EMAIL_PASS))
        server.send_message(message)