# Redis Roadmap for IMS

## ✅ Completed

- [x] Rate Limiter
  - Prevent brute-force attacks
  - Prevent API abuse
  - TTL-based counters

---

## 🔜 Next Features

### 1. OTP Storage
- Store email/phone OTP
- Auto expire (5-10 min)
- Delete after verification

---

### 2. Email Queue
- Queue welcome emails
- Password reset emails
- Invoice emails
- Notification emails
- Scheduler/Worker processes queue

---

### 3. Background Job Queue
- CSV Import
- CSV Export
- Bulk Product Update
- Bulk Category Update
- Image Processing
- Long-running reports

---

### 4. Caching
- Dashboard statistics
- Product details
- Categories
- User profile
- User permissions
- Subscription details
- Business settings
- Frequently used reports

---

### 5. Distributed Locks
- Scheduler lock
- Cleanup lock
- Report generation lock
- Payment processing lock
- Import/Export lock

---

### 6. Payment Lock
- Prevent duplicate payments
- Prevent double-click checkout
- Prevent duplicate webhook processing

---

### 7. Inventory Reservation (Future)
- Reserve stock during checkout
- Auto release after timeout
- Prevent overselling

---

### 8. Analytics Counters
- Today's Sales
- Today's Revenue
- Today's Orders
- Active Users
- Login Count
- Product Views

---

### 9. Session Store (Optional)
- Logout from all devices
- Token blacklist
- Device sessions
- Refresh token management

---

### 10. Notification Queue
- Email
- WhatsApp
- SMS
- Push Notifications
- In-App Notifications

---

### 11. Search Cache
- Product search
- Category search
- Frequently searched keywords

---

### 12. API Response Cache
- Frequently used GET endpoints
- Dashboard APIs
- Reports APIs

---

### 13. Temporary File Storage
- CSV import progress
- Export status
- Generated report status

---

### 14. User Presence (Future)
- Online users
- Last seen
- Active sessions

---

### 15. Feature Flags
- Enable/Disable features
- Beta features
- Trial features
- Plan-based feature access

---

### 16. Real-time Dashboard
- Live sales counter
- Live revenue
- Live notifications
- Live order count

---

### 17. Distributed Event Bus (Future)
- Product Created
- Sale Completed
- Payment Successful
- User Registered
- Trigger background services

---

### 18. Idempotency Keys
- Prevent duplicate API requests
- Safe retry support
- Payment retries

---

## Redis Folder Structure (Future)

services/
└── redis/
    ├── cache.py
    ├── queue.py
    ├── otp.py
    ├── locks.py
    ├── counters.py
    ├── sessions.py
    ├── events.py
    ├── idempotency.py
    ├── keys.py
    └── client.py