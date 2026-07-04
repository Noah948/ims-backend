# this file contains the rate limit policies for different endpoints in the application
# change limit here to see the effect of rate limiting on the endpoints

from dataclasses import dataclass

@dataclass(frozen=True)
class RateLimitPolicy:
    limit: int
    window: int  # seconds
    key_prefix: str


class AuthRateLimits:
    LOGIN = RateLimitPolicy(
        limit=5,
        window=60,
        key_prefix="login",
    )

    REGISTER = RateLimitPolicy(
        limit=3,
        window=3600,
        key_prefix="register",
    )

    PASSWORD_RESET = RateLimitPolicy(
        limit=3,
        window=3600,
        key_prefix="password-reset",
    )


class ApiRateLimits:
    GENERAL = RateLimitPolicy(
        limit=100,
        window=60,
        key_prefix="api",
    )

    ADMIN = RateLimitPolicy(
        limit=300,
        window=60,
        key_prefix="admin",
    )