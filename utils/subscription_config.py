# Subscription lifecycle configuration
# Change these values here when business rules change.


# curretnly the naming is not upto mark, it should be much easier to understand
# later if you wish to change the naming,
# make sure to update the references in the subscription job
RENEWAL_REMINDER_DAYS = 2
GRACE_PERIOD_DAYS = 3
FINAL_WARNING_DAYS_BEFORE_GRACE_END = 1
DELETION_WARNING_DAYS_AFTER_BLOCK = 30
PERMANENT_DELETION_DAYS_AFTER_WARNING = 7