# here we define the RateLimiter class that will be used to check if a user is allowed to make a request based on the rate limit policies defined in policies.py

# redis key format: {key_prefix}:{identifier} -> count of requests
# example: login:user123 -> 3 (3 requests made by user123 to the login endpoint)


from core.redis import redis_client
from .policies import RateLimitPolicy

class RateLimiter:

    def is_allowed(self, identifier: str, policy: RateLimitPolicy) -> tuple[bool, int]:

        key = f"{policy.key_prefix}:{identifier}"

        pipe = redis_client.pipeline()

        pipe.incr(key)
        pipe.expire(key, policy.window, nx=True)

        current_requests, _ = pipe.execute()

        if current_requests > policy.limit:
            retry_after = redis_client.ttl(key)
            return False, retry_after

        return True, 0

rate_limiter = RateLimiter()