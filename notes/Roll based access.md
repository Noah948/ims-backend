Perfect—let’s do this **clean, step-by-step, no fluff** 👇

---

# ✅ Step 1: Add role column to User model

```python
role = Column(String, default="staff")
```

👉 Run migration / update DB

---

# ✅ Step 2: Ensure role is included in response

In your response schema:

```python
role: str
```

👉 And return it in login / user response

---

# ✅ Step 3: Create permissions file

📁 `app/core/permissions.py`

```python
ROLE_PERMISSIONS = {
    "owner": ["create", "read", "update", "delete"],
    "staff": ["read"]
}
```

---

# ✅ Step 4: Create permission dependency

```python
from fastapi import Depends, HTTPException
from app.core.permissions import ROLE_PERMISSIONS
from app.dependencies.auth import get_current_user

def require_permission(permission: str):
    def checker(current_user = Depends(get_current_user)):
        if permission not in ROLE_PERMISSIONS.get(current_user.role, []):
            raise HTTPException(status_code=403, detail="Not allowed")
        return current_user
    return checker
```

---

# ✅ Step 5: Use in routes

```python
@router.post("/products")
def create_product(user = Depends(require_permission("create"))):
    ...
```

```python
@router.get("/products")
def get_products(user = Depends(require_permission("read"))):
    ...
```

---

# ✅ Step 6: Set default role on user creation

```python
new_user.role = "staff"
```

(or rely on DB default)

---

# ✅ Step 7: Test

* Login as **owner** → all routes work
* Login as **staff** → restricted routes → **403**

---

# ✅ Done ✔️

That’s your **complete backend RBAC (simple + production-safe)**

---

If something breaks, next step is:
👉 check `get_current_user` returns correct role

