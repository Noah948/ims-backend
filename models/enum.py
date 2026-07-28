from enum import Enum


class MemberRole(str, Enum):
    OWNER = "OWNER"
    OPERATOR = "OPERATOR"


class SubscriptionPlan(str, Enum):
    TRIAL = "TRIAL"
    BASIC = "BASIC"
    LIFETIME = "LIFETIME"


class SubscriptionStatus(str, Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"