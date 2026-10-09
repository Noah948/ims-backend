
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


# =====================================================
# EMAIL CONFIGURATION
# =====================================================

EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

if not EMAIL_USER or not EMAIL_PASS:
    raise ValueError(
        "EMAIL_USER and EMAIL_PASS environment variables must be set"
    )


# =====================================================
# OTP EMAIL
# =====================================================

def send_otp_email(
    email: str,
    otp: str,
    purpose: str,
):

    # -------------------------------------------------
    # Dynamic content based on purpose
    # -------------------------------------------------

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

    # -------------------------------------------------
    # Common HTML template
    # -------------------------------------------------

    html_content = f"""
    <html>
    <body style="
        margin:0;
        padding:0;
        font-family: Arial, sans-serif;
        background-color:#f4f4f4;
    ">

        <div style="
            max-width:500px;
            margin:40px auto;
            background:white;
            padding:30px;
            border-radius:10px;
            text-align:center;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
        ">

            <h2 style="color:#333;">
                {title}
            </h2>

            <p style="
                color:#555;
                font-size:14px;
            ">
                {message}
            </p>

            <div style="
                margin:20px 0;
                font-size:28px;
                font-weight:bold;
                letter-spacing:5px;
                color:#2d89ef;
            ">
                {otp}
            </div>

            <p style="
                color:#777;
                font-size:13px;
            ">
                This OTP is valid for <b>10 minutes</b>.
            </p>

            <hr style="
                margin:25px 0;
                border:none;
                border-top:1px solid #eee;
            ">

            <p style="
                color:#999;
                font-size:12px;
            ">
                If you didn’t request this,
                you can safely ignore this email.
            </p>

        </div>

    </body>
    </html>
    """

    # -------------------------------------------------
    # Email setup
    # -------------------------------------------------

    message_obj = MIMEMultipart("alternative")

    message_obj["Subject"] = subject
    message_obj["From"] = EMAIL_USER
    message_obj["To"] = email

    message_obj.attach(
        MIMEText(html_content, "html")
    )

    # -------------------------------------------------
    # Send email
    # -------------------------------------------------

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
    ) as server:

        server.login(
            EMAIL_USER,
            EMAIL_PASS,
        )

        server.send_message(message_obj)


# =====================================================
# EMAIL VERIFICATION
# =====================================================

def send_verification_email(
    email: str,
    token: str,
):
    """
    Send email verification link.

    The user clicks the link and the browser automatically
    calls the FastAPI verification endpoint.

    Backend route:

        GET /users/verify-email?token=...

    """

    # -------------------------------------------------
    # Create clickable verification URL
    # -------------------------------------------------

    verification_link = (
        f"{FRONTEND_URL}"
        f"/verify-email"
        f"?token={token}"
    )

    # -------------------------------------------------
    # Verification email HTML
    # -------------------------------------------------

    html_content = f"""
    <html>

    <body style="
        margin:0;
        padding:0;
        font-family: Arial, sans-serif;
        background-color:#f4f4f4;
    ">

        <div style="
            max-width:500px;
            margin:40px auto;
            background:white;
            padding:30px;
            border-radius:10px;
            text-align:center;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
        ">

            <h2 style="
                color:#333;
            ">
                Verify Your Email
            </h2>

            <p style="
                color:#555;
                font-size:14px;
                margin-bottom:30px;
            ">
                Thank you for registering.
                Click the button below to verify your email address.
            </p>

            <a
                href="{verification_link}"
                style="
                    display:inline-block;
                    padding:14px 28px;
                    background-color:#2d89ef;
                    color:white;
                    text-decoration:none;
                    border-radius:6px;
                    font-weight:bold;
                    font-size:16px;
                "
            >
                Verify Email
            </a>

            <p style="
                color:#777;
                font-size:13px;
                margin-top:30px;
            ">
                This verification link is valid for
                <b>15 minutes</b>.
            </p>

            <hr style="
                margin:25px 0;
                border:none;
                border-top:1px solid #eee;
            ">

            <p style="
                color:#999;
                font-size:12px;
            ">
                If you didn’t create this account,
                you can safely ignore this email.
            </p>

        </div>

    </body>

    </html>
    """

    # -------------------------------------------------
    # Email setup
    # -------------------------------------------------

    message_obj = MIMEMultipart("alternative")

    message_obj["Subject"] = "Verify Your Email"
    message_obj["From"] = EMAIL_USER
    message_obj["To"] = email

    message_obj.attach(
        MIMEText(
            html_content,
            "html",
        )
    )

    # -------------------------------------------------
    # Send email
    # -------------------------------------------------

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
    ) as server:

        server.login(
            EMAIL_USER,
            EMAIL_PASS,
        )

        server.send_message(message_obj)


# =====================================================
# SUBSCRIPTION EMAILS
# =====================================================

SUBSCRIPTION_TEMPLATE_DIR = (
    Path(__file__).resolve().parent
    / "email_templates"
    / "subscription"
)


def _load_email_template(
    template_name: str,
    **context,
) -> str:

    template_path = (
        SUBSCRIPTION_TEMPLATE_DIR
        / template_name
    )

    if not template_path.exists():

        raise FileNotFoundError(
            f"Email template not found: {template_path}"
        )

    html_content = template_path.read_text(
        encoding="utf-8"
    )

    for key, value in context.items():

        html_content = html_content.replace(
            "{{ " + key + " }}",
            str(value),
        )

    return html_content


def _send_html_email(
    email: str,
    subject: str,
    html_content: str,
):

    message_obj = MIMEMultipart("alternative")

    message_obj["Subject"] = subject
    message_obj["From"] = EMAIL_USER
    message_obj["To"] = email

    message_obj.attach(
        MIMEText(
            html_content,
            "html",
        )
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
    ) as server:

        server.login(
            EMAIL_USER,
            EMAIL_PASS,
        )

        server.send_message(message_obj)


def send_subscription_renewal_email(
    email: str,
    owner_name: str,
    business_name: str,
    subscription_end,
):

    html_content = _load_email_template(
        "renewal_reminder.html",
        owner_name=owner_name,
        business_name=business_name,
        subscription_end=subscription_end,
    )

    _send_html_email(
        email=email,
        subject="Your Subscription Is Ending Soon",
        html_content=html_content,
    )


def send_subscription_final_warning_email(
    email: str,
    owner_name: str,
    business_name: str,
    grace_end,
):

    html_content = _load_email_template(
        "final_warning.html",
        owner_name=owner_name,
        business_name=business_name,
        grace_end=grace_end,
    )

    _send_html_email(
        email=email,
        subject="Subscription Renewal Required",
        html_content=html_content,
    )


def send_subscription_deletion_warning_email(
    email: str,
    owner_name: str,
    business_name: str,
    permanent_deletion_date,
):

    html_content = _load_email_template(
        "deletion_warning.html",
        owner_name=owner_name,
        business_name=business_name,
        permanent_deletion_date=permanent_deletion_date,
    )

    _send_html_email(
        email=email,
        subject="Your Business Is Scheduled for Deletion",
        html_content=html_content,
    )

