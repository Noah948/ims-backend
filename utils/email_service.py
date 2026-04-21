import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")

if not EMAIL_USER or not EMAIL_PASS:
    raise ValueError("EMAIL_USER and EMAIL_PASS environment variables must be set")


def send_otp_email(email: str, otp: str, purpose: str):

    # 🎯 Dynamic content based on purpose
    if purpose == "PASSWORD_RESET":
        subject = "Reset your password"
        title = "Password Reset"
        message = "Use the OTP below to reset your password."

    elif purpose == "ACCOUNT_DELETE":
        subject = "Confirm Account Deletion"
        title = "Delete Account"
        message = "Use the OTP below to confirm your account deletion."

    else:
        subject = "Your OTP"
        title = "Verification"
        message = "Use the OTP below for verification."

    # 📧 Common HTML template
    html_content = f"""
    <html>
    <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color:#f4f4f4;">
        <div style="max-width:500px; margin:40px auto; background:white; padding:30px; border-radius:10px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,0.1);">
            
            <h2 style="color:#333;">{title}</h2>
            
            <p style="color:#555; font-size:14px;">
                {message}
            </p>

            <div style="margin:20px 0; font-size:28px; font-weight:bold; letter-spacing:5px; color:#2d89ef;">
                {otp}
            </div>

            <p style="color:#777; font-size:13px;">
                This OTP is valid for <b>10 minutes</b>.
            </p>

            <hr style="margin:25px 0; border:none; border-top:1px solid #eee;">

            <p style="color:#999; font-size:12px;">
                If you didn’t request this, you can safely ignore this email.
            </p>
        </div>
    </body>
    </html>
    """

    # 📦 Email setup
    message_obj = MIMEMultipart("alternative")
    message_obj["Subject"] = subject
    message_obj["From"] = EMAIL_USER
    message_obj["To"] = email

    message_obj.attach(MIMEText(html_content, "html"))

    # 🚀 Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(message_obj)