from core.database import SessionLocal

from services.product_service import cleanup_deleted_products
from services.category_service import cleanup_deleted_categories
from services.expense_service import cleanup_deleted_expenses
from services.audit_log_service import cleanup_deleted_audit_logs


CLEANUP_TASKS = [
    cleanup_deleted_products,
    cleanup_deleted_categories,
    cleanup_deleted_expenses,
    cleanup_deleted_audit_logs,
]


def cleanup_job():
    db = SessionLocal()

    try:
        for task in CLEANUP_TASKS:
            task(db)

    except Exception as e:
        print(f"Cleanup job failed: {e}")

    finally:
        db.close()

def register_cleanup_jobs(scheduler):
    scheduler.add_job(
        cleanup_job,
        trigger="cron",
        hour=2,
        minute=0,

        # Testing:
        # trigger="interval",
        # seconds=10,

        id="cleanup_job",
        replace_existing=True,
    )