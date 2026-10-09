from sqlalchemy import text

from core.database import SessionLocal


# Raw SQL on purpose: one statement for all businesses, and it bypasses the
# ORM audit listener (snapshots aren't user actions).
SNAPSHOT_SQL = text("""
    INSERT INTO inventory_snapshots
        (business_id, snapshot_date, total_units, stock_value, low_stock, out_of_stock)
    SELECT
        b.id,
        (now() AT TIME ZONE 'Asia/Kolkata')::date,
        COALESCE(SUM(p.stock), 0),
        COALESCE(SUM(p.stock * p.price), 0),
        b.low_stock_products,
        b.out_of_stock_products
    FROM businesses b
    LEFT JOIN products p
        ON p.business_id = b.id AND p.deleted_at IS NULL
    WHERE b.deleted_at IS NULL
    GROUP BY b.id
    ON CONFLICT (business_id, snapshot_date) DO NOTHING
""")


def inventory_snapshot_job():
    db = SessionLocal()

    try:
        db.execute(SNAPSHOT_SQL)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Inventory snapshot job failed: {e}")

    finally:
        db.close()


def register_snapshot_jobs(scheduler):
    scheduler.add_job(
        inventory_snapshot_job,
        trigger="cron",
        hour=23,
        minute=55,
        id="inventory_snapshot_job",
        replace_existing=True,
    )
