# this file is used to connect fastapi endpoints with the rate limiter. It defines a dependency that can be used in the endpoints to enforce rate limiting based on the policies defined in policies.py

#                                Client
#                                    │
#                                    ▼
#                                FastAPI Router
#                                    │
#                                    ▼
#                                Resolve Dependencies
#                                    │
#                                    ▼
#                                rate_limit(AuthRateLimits.LOGIN)
#                                    │
#                                    ▼
#                                dependency(request)
#                                    │
#                                    ▼
#                                rate_limiter.is_allowed()
#                                    │
#                                    ▼
#                                Redis
#                                    │
#                                    ├── INCR key
#                                    ├── EXPIRE key
#                                    └── TTL (if needed)
#                                    │
#                                    ▼
#                                Allowed?
#                                    │
#                                 ┌──┴─────────────┐
#                                 │                │
#                                Yes              No
#                                 │                │
#                                 ▼                ▼
#                                Login Route     HTTP 429
#                                Executes        Returned
#                                 │
#                                 ▼
#                                Response

from collections.abc import Callable

from fastapi import HTTPException, Request

from .limiter import rate_limiter
from .policies import RateLimitPolicy
from .identifiers import client_ip


def rate_limit(
    policy: RateLimitPolicy,
    identifier: Callable[[Request], str] = client_ip,
):

    async def dependency(request: Request):

        key = identifier(request)

        allowed, retry_after = rate_limiter.is_allowed(
            identifier=key,
            policy=policy,
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Try again in {retry_after} seconds.",
                headers={
                    "Retry-After": str(retry_after)
                },
            )

    return dependency