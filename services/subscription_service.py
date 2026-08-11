from datetime import datetime, timedelta

from models.business import Business
from models.enums import SubscriptionPlan, SubscriptionStatus

from utils.subscription_config import (
    GRACE_PERIOD_DAYS,
    FINAL_WARNING_DAYS_BEFORE_GRACE_END,
    DELETION_WARNING_DAYS_AFTER_BLOCK,
    PERMANENT_DELETION_DAYS_AFTER_WARNING,
)


def get_grace_period_end(business: Business) -> datetime | None:
    """
    Return the date/time when the grace period ends.
    """
    if not business.subscription_end:
        return None

    if business.subscription_plan == SubscriptionPlan.LIFETIME:
        return None

    return business.subscription_end + timedelta(
        days=GRACE_PERIOD_DAYS
    )


def get_final_warning_date(business: Business) -> datetime | None:
    """
    Return the date/time when the final renewal warning should be sent.
    """
    grace_end = get_grace_period_end(business)

    if not grace_end:
        return None

    return grace_end - timedelta(
        days=FINAL_WARNING_DAYS_BEFORE_GRACE_END
    )


def get_deletion_warning_date(business: Business) -> datetime | None:
    """
    Return the date/time when the deletion warning should be sent.
    """
    grace_end = get_grace_period_end(business)

    if not grace_end:
        return None

    return grace_end + timedelta(
        days=DELETION_WARNING_DAYS_AFTER_BLOCK
    )


def get_permanent_deletion_date(business: Business) -> datetime | None:
    """
    Return the date/time when the business should be permanently deleted.
    """
    deletion_warning_date = get_deletion_warning_date(business)

    if not deletion_warning_date:
        return None

    return deletion_warning_date + timedelta(
        days=PERMANENT_DELETION_DAYS_AFTER_WARNING
    )


def is_subscription_expired(business: Business) -> bool:
    """
    Check whether the paid/trial subscription period has ended.
    Lifetime businesses never expire.
    """
    if business.subscription_plan == SubscriptionPlan.LIFETIME:
        return False

    if not business.subscription_end:
        return False

    return datetime.utcnow() >= business.subscription_end


def is_in_grace_period(business: Business) -> bool:
    """
    Check whether the business is currently inside its grace period.
    """
    if business.subscription_plan == SubscriptionPlan.LIFETIME:
        return False

    if not business.subscription_end:
        return False

    now = datetime.utcnow()
    grace_end = get_grace_period_end(business)

    return (
        business.subscription_end <= now < grace_end
    )


def should_block_access(business: Business) -> bool:
    """
    Access is blocked after the grace period ends.
    """
    if business.subscription_plan == SubscriptionPlan.LIFETIME:
        return False

    if not business.subscription_end:
        return False

    grace_end = get_grace_period_end(business)

    return datetime.utcnow() >= grace_end