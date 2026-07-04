Right now, your rate limiter is **IP-based**. That means you simply choose a policy and attach it to the route.

---

## 1. Authentication routes

### Login

```python
@router.post(
    "/login",
    dependencies=[Depends(rate_limit(AuthRateLimits.LOGIN))]
)
```

---

### Register

```python
@router.post(
    "/register",
    dependencies=[Depends(rate_limit(AuthRateLimits.REGISTER))]
)
```

---

### Password Reset

```python
@router.post(
    "/forgot-password",
    dependencies=[Depends(rate_limit(AuthRateLimits.PASSWORD_RESET))]
)
```

---

## 2. General APIs

For endpoints like:

* Products
* Categories
* Sales
* Expenses

use:

```python
dependencies=[Depends(rate_limit(ApiRateLimits.GENERAL))]
```

Example:

```python
@router.get(
    "/products",
    dependencies=[Depends(rate_limit(ApiRateLimits.GENERAL))]
)
```

---

## 3. Admin-only APIs

For expensive operations like:

* Import CSV
* Generate reports
* Analytics
* Bulk update

use:

```python
dependencies=[Depends(rate_limit(ApiRateLimits.ADMIN))]
```

---

## 4. Creating new policies

Whenever you need a different limit, just add it to `policies.py`.

Example:

```python
class ApiRateLimits:

    EXPORT = RateLimitPolicy(
        limit=10,
        window=3600,
        key_prefix="export",
    )
```

Then:

```python
@router.get(
    "/export",
    dependencies=[Depends(rate_limit(ApiRateLimits.EXPORT))]
)
```

---

## The beauty of this design

You **never touch**:

* `limiter.py`
* `dependency.py`
* `redis.py`

You only:

1. Add a policy.
2. Attach it to a route.

That's exactly the modularity we were aiming for. Later, when we improve the limiter (better algorithms, proxy support, email-based checks, etc.), **all your existing routes will continue to work without any changes.**
