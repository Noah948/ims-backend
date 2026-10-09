"""
Retention policies for soft-deleted records.

All values are in days.
"""

PRODUCT_RETENTION_DAYS = 30
CATEGORY_RETENTION_DAYS = 30
EXPENSE_RETENTION_DAYS = 90
AUDIT_LOG_RETENTION_DAYS = 365

# policies related to subscription lifecycle are in utils/subscription_config.py
# they are not here since they are used in subscriptio service also