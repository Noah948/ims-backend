Since your backend is already structured (models, services, routes, utils, etc.), the **forgot-password + email OTP system** should be added in a clean modular way so it doesn’t clutter your auth logic.

I’ll show you:

1. **Folder / file structure**
2. **SMTP setup steps**
3. **Database table needed**
4. **API endpoints**
5. Small code snippets where useful

This will fit well with your current FastAPI architecture.

---

# 1. Folder & File Structure to Add

Inside your backend project add these files.

```
backend/
│
├── models/
│   └── password_reset_otp.py
│
├── schemas/
│   └── password_reset.py
│
├── services/
│   └── password_reset_service.py
│
├── routes/
│   └── password_reset_routes.py
│
├── utils/
│   ├── email_service.py
│   └── otp_generator.py
│
├── core/
│   └── config.py
│
└── .env
```

Purpose of each file:

| File                      | Purpose                  |
| ------------------------- | ------------------------ |
| password_reset_otp.py     | DB table storing OTP     |
| password_reset.py         | request/response schemas |
| password_reset_service.py | main logic               |
| password_reset_routes.py  | API endpoints            |
| email_service.py          | SMTP email sender        |
| otp_generator.py          | generate OTP             |
| config.py                 | environment variables    |
| .env                      | Gmail credentials        |

---

# 2. Database Table Needed

Create a table for OTP storage.

Example structure:

```
password_reset_otps

id
email
otp
expires_at
created_at
is_used
```

Important rules:

```
OTP expiry = 10 minutes
Delete or mark used after success
```

---

# 3. API Endpoints You Need

You only need **three endpoints**.

### 1️⃣ Request OTP

```
POST /auth/forgot-password
```

Input:

```
{
 "email": "user@mail.com"
}
```

Backend will:

```
check user exists
generate OTP
store in DB
send email
```

---

### 2️⃣ Verify OTP

```
POST /auth/verify-otp
```

Input:

```
{
 "email": "user@mail.com",
 "otp": "123456"
}
```

Backend will:

```
check otp
check expiry
allow reset
```

---

### 3️⃣ Reset Password

```
POST /auth/reset-password
```

Input:

```
{
 "email": "...",
 "otp": "...",
 "new_password": "..."
}
```

Backend will:

```
verify otp
hash new password
update user password
mark OTP used
```

---

# 4. Gmail SMTP Setup Steps

Create a **new Gmail account for the application**.

Example:

```
ims.backend.service@gmail.com
```

Then do this.

### Step 1 — Enable 2-Step Verification

Go to:

```
Google Account
→ Security
→ 2-Step Verification
```

Enable it.

---

### Step 2 — Generate App Password

Go to:

```
Google Account
→ Security
→ App Passwords
```

Choose:

```
App: Mail
Device: Other
```

Google gives:

```
abcd efgh ijkl mnop
```

This is the password your backend will use.

---

### Step 3 — Add environment variables

Create `.env`

```
EMAIL_USER=ims.backend.service@gmail.com
EMAIL_PASS=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
```

---

### Step 4 — Load variables in config

Inside:

```
core/config.py
```

You load `.env` values.

---

# 5. Email Service Utility

Create:

```
utils/email_service.py
```

Purpose:

```
send_otp_email()
send_reset_email()
```

This keeps email logic separate from routes.

---

# 6. OTP Generator Utility

Create:

```
utils/otp_generator.py
```

Example code (small so I’ll include it):

```python
import random

def generate_otp():
    return str(random.randint(100000, 999999))
```

---

# 7. Email Sending Code (SMTP)

Since this is small, here is the full function.

File:

```
utils/email_service.py
```

```python
import smtplib
from email.mime.text import MIMEText
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_otp_email(receiver_email, otp):

    message = MIMEText(f"Your password reset OTP is: {otp}")
    message["Subject"] = "Password Reset OTP"
    message["From"] = EMAIL_USER
    message["To"] = receiver_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    server.login(EMAIL_USER, EMAIL_PASS)

    server.send_message(message)

    server.quit()
```

---

# 8. OTP Expiry Logic

Inside service logic:

```
expires_at = now + 10 minutes
```

Example concept:

```
if current_time > expires_at:
    OTP invalid
```

---

# 9. Security Rules (Very Important)

Add these protections.

Limit OTP requests:

```
max 3 OTP per hour
```

OTP expiry:

```
10 minutes
```

OTP attempts:

```
max 5 tries
```

---

# 10. Clean Architecture Flow

Your system will look like this.

```
Route
  ↓
Service
  ↓
OTP Generator
  ↓
DB Save
  ↓
Email Service
  ↓
SMTP Gmail
  ↓
User Mailbox
```

---

# 11. Final Structure (Clean View)

```
backend
│
├── models
│   └── password_reset_otp.py
│
├── schemas
│   └── password_reset.py
│
├── services
│   └── password_reset_service.py
│
├── routes
│   └── password_reset_routes.py
│
├── utils
│   ├── email_service.py
│   └── otp_generator.py
│
├── core
│   └── config.py
│
└── .env
```

---

When you're ready, next I can give you **production-ready code for all files**:

* OTP model
* schemas
* service logic
* FastAPI routes
* password reset flow

It will fit directly into your **existing backend architecture** so you can just plug it in.
