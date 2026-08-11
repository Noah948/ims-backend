from datetime import datetime, timedelta

from core.database import SessionLocal
from models.business import Business

from utils.subscription_config import (
    RENEWAL_REMINDER_DAYS,
    GRACE_PERIOD_DAYS,
    DELETION_WARNING_DAYS_AFTER_BLOCK,
    PERMANENT_DELETION_DAYS_AFTER_WARNING,
)


def subscription_job():
    db = SessionLocal()

    try:
        now = datetime.utcnow()

        businesses = (
            db.query(Business)
            .filter(
                Business.deleted_at.is_(None),
                Business.subscription_end.isnot(None),
            )
            .all()
        )

        for business in businesses:

            subscription_end = business.subscription_end

            reminder_date = (
                subscription_end
                - timedelta(days=RENEWAL_REMINDER_DAYS)
            )

            grace_end = (
                subscription_end
                + timedelta(days=GRACE_PERIOD_DAYS)
            )

            deletion_warning_date = (
                grace_end
                + timedelta(days=DELETION_WARNING_DAYS_AFTER_BLOCK)
            )

            permanent_deletion_date = (
                deletion_warning_date
                + timedelta(days=PERMANENT_DELETION_DAYS_AFTER_WARNING)
            )

            print(
                f"""
            ==================================================
            BUSINESS SUBSCRIPTION
            ==================================================
            Business ID       : {business.id}

            Subscription End  : {subscription_end}
            Renewal Reminder  : {reminder_date}
            Grace Period Ends : {grace_end}
            Deletion Warning  : {deletion_warning_date}
            Permanent Delete  : {permanent_deletion_date}
            ==================================================
            """
            )

    except Exception as e:
        print(f"Subscription job failed: {e}")

    finally:
        db.close()


def register_subscription_jobs(scheduler):

    # use this for real working process, this will run the job every day at 2:00 AM
    # scheduler.add_job(
    #     subscription_job,
    #     trigger="cron",
    #     hour=2,
    #     minute=0,
    #     id="subscription_job",
    #     replace_existing=True,
    # )


    # use this for testing, this will run the job every 10 seconds
    scheduler.add_job(
        subscription_job,
        trigger="interval",
        seconds=10,
        id="subscription_job",
        replace_existing=True,
    )