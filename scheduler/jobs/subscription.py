from datetime import datetime, timedelta

from core.database import SessionLocal
from models.business import Business
from models.user_model import User

from utils.email_service import (
    send_subscription_renewal_email,
    send_subscription_deletion_warning_email,
    send_subscription_final_warning_email,
)

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
                + timedelta(
                    days=PERMANENT_DELETION_DAYS_AFTER_WARNING
                )
            )

            # ---------------------------------------------
            # Get business owner
            # ---------------------------------------------

            owner = (
                db.query(User)
                .filter(
                    User.id == business.owner_id,
                    User.deleted_at.is_(None),
                )
                .first()
            )

            if not owner:
                print(
                    f"Owner not found for business {business.id}"
                )
                continue

            # ---------------------------------------------
            # Renewal reminder
            # ---------------------------------------------

            if (
                now >= reminder_date
                and now < subscription_end
                and not business.renewal_reminder_sent
            ):
                try:
                    send_subscription_renewal_email(
                        email=owner.email,
                        owner_name=owner.full_name,
                        business_name=business.name,
                        subscription_end=subscription_end,
                    )

                    business.renewal_reminder_sent = True

                    print(
                        f"Renewal reminder sent to {owner.email} "
                        f"for business {business.id}"
                    )

                except Exception as e:
                    print(
                        f"Failed to send renewal reminder "
                        f"for business {business.id}: {e}"
                    )

            # ---------------------------------------------
            # Final warning
            # ---------------------------------------------

            if (
                now >= deletion_warning_date
                and now < permanent_deletion_date
                and not business.final_warning_sent
            ):
                try:
                    send_subscription_final_warning_email(
                        email=owner.email,
                        owner_name=owner.full_name,
                        business_name=business.name,
                        grace_end=grace_end,
                    )

                    business.final_warning_sent = True

                    print(
                        f"Final warning sent to {owner.email} "
                        f"for business {business.id}"
                    )

                except Exception as e:
                    print(
                        f"Failed to send final warning "
                        f"for business {business.id}: {e}"
                    )

            # ---------------------------------------------
            # Deletion warning
            # ---------------------------------------------

            if (
                now >= permanent_deletion_date
                and not business.deletion_warning_sent
            ):
                try:
                    send_subscription_deletion_warning_email(
                        email=owner.email,
                        owner_name=owner.full_name,
                        business_name=business.name,
                        permanent_deletion_date=permanent_deletion_date,
                    )

                    business.deletion_warning_sent = True

                    print(
                        f"Deletion warning sent to {owner.email} "
                        f"for business {business.id}"
                    )

                except Exception as e:
                    print(
                        f"Failed to send deletion warning "
                        f"for business {business.id}: {e}"
                    )

            db.commit()

    except Exception as e:
        db.rollback()
        print(f"Subscription job failed: {e}")

    finally:
        db.close()      


def register_subscription_jobs(scheduler):

    scheduler.add_job(
        subscription_job,
        trigger="interval",
        seconds=10,
        id="subscription_job",
        replace_existing=True,
    )