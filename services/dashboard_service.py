from datetime import date, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlalchemy.orm import Session

from core.redis import redis_client
from models.business import Business
from schema.dashboard import DashboardRange, DashboardResponse


IST = ZoneInfo("Asia/Kolkata")
CACHE_TTL_SECONDS = 300

# Timestamps are naive in the DB session's timezone. These convert between
# that and IST in SQL so day/hour buckets match the shop's local time.
# Bounds are converted on the parameter side so (business_id, created_at)
# stays index-usable.
LOCAL_TS = "(s.created_at AT TIME ZONE current_setting('TimeZone') AT TIME ZONE 'Asia/Kolkata')"
START = "(CAST(:start AS timestamp) AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE current_setting('TimeZone'))"
END = "(CAST(:end AS timestamp) AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE current_setting('TimeZone'))"
IN_RANGE = f"s.business_id = :bid AND s.created_at >= {START} AND s.created_at < {END}"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _cache_key(business_id: UUID) -> str:
    return f"dash:{business_id}"


def invalidate_dashboard(business_id: UUID) -> None:
    try:
        redis_client.delete(_cache_key(business_id))
    except Exception as e:
        print(f"Dashboard cache invalidation failed: {e}")


def _range_bounds(range_: DashboardRange, today: date) -> tuple[datetime, datetime, str]:
    """Returns IST-naive [start, end) and the trend bucket size."""
    end = datetime.combine(today + timedelta(days=1), datetime.min.time())
    if range_ == "today":
        return datetime.combine(today, datetime.min.time()), end, "hour"
    if range_ == "7d":
        return datetime.combine(today - timedelta(days=6), datetime.min.time()), end, "day"
    if range_ == "month":
        return datetime.combine(today.replace(day=1), datetime.min.time()), end, "day"
    return datetime.combine(today.replace(month=1, day=1), datetime.min.time()), end, "month"


def _buckets(start: datetime, today: date, now_hour: int, bucket: str) -> list[tuple[object, str]]:
    """Every bucket key in the range with its chart label, so empty periods show as 0."""
    if bucket == "hour":
        return [(h, f"{h:02d}:00") for h in range(now_hour + 1)]
    if bucket == "day":
        days = (today - start.date()).days + 1
        return [
            (d, d.strftime("%d %b"))
            for d in (start.date() + timedelta(days=i) for i in range(days))
        ]
    return [(m, MONTHS[m - 1]) for m in range(1, today.month + 1)]


def mask_contact(contact: str) -> str:
    if len(contact) < 4:
        return contact
    return contact[:2] + "x" * (len(contact) - 4) + contact[-2:]


def _f(value) -> float:
    return float(value or 0)


def get_dashboard(
    db: Session,
    business: Business,
    range_: DashboardRange,
    is_owner: bool,
) -> DashboardResponse:
    key = _cache_key(business.id)
    field = f"{range_}:{'owner' if is_owner else 'operator'}"

    try:
        cached = redis_client.hget(key, field)
        if cached:
            return DashboardResponse.model_validate_json(cached)
    except Exception as e:
        print(f"Dashboard cache read failed: {e}")

    result = _compute_dashboard(db, business, range_, is_owner)

    try:
        redis_client.hset(key, field, result.model_dump_json())
        redis_client.expire(key, CACHE_TTL_SECONDS)
    except Exception as e:
        print(f"Dashboard cache write failed: {e}")

    return result


def _compute_dashboard(
    db: Session,
    business: Business,
    range_: DashboardRange,
    is_owner: bool,
) -> DashboardResponse:
    now = datetime.now(IST)
    today = now.date()
    start, end, bucket = _range_bounds(range_, today)
    p = {"bid": business.id, "start": start, "end": end}

    def rows(sql: str, **extra):
        return db.execute(text(sql), {**p, **extra}).mappings().all()

    def one(sql: str, **extra):
        return db.execute(text(sql), {**p, **extra}).mappings().one()

    # ---------------- Summary ----------------
    sales = one(f"""
        SELECT COALESCE(SUM(s.total_amount), 0) AS revenue,
               COALESCE(SUM(s.total_profit), 0) AS profit,
               COUNT(*) AS orders
        FROM sales s WHERE {IN_RANGE}
    """)

    units = one(f"""
        SELECT COALESCE(SUM(si.quantity), 0) AS sold,
               COALESCE(SUM(si.returned_quantity), 0) AS returned
        FROM sale_items si JOIN sales s ON s.id = si.sale_id
        WHERE {IN_RANGE}
    """)

    customers = one(f"""
        SELECT COUNT(*) AS unique_customers,
               COUNT(*) FILTER (WHERE n > 1) AS repeat_customers
        FROM (
            SELECT customer_contact, COUNT(*) AS n
            FROM sales s WHERE {IN_RANGE}
            GROUP BY customer_contact
        ) c
    """)

    revenue = _f(sales["revenue"])
    orders = int(sales["orders"])
    sold = int(units["sold"])
    returned = int(units["returned"])

    summary = {
        "revenue": revenue,
        "orders": orders,
        "avg_order_value": revenue / orders if orders else 0,
        "units_sold": sold - returned,
        "return_rate": returned * 100 / sold if sold else 0,
        "unique_customers": int(customers["unique_customers"]),
        "repeat_customers": int(customers["repeat_customers"]),
    }

    if is_owner:
        expenses = _f(one("""
            SELECT COALESCE(SUM(amount), 0) AS total FROM expenses
            WHERE business_id = :bid AND deleted_at IS NULL
              AND expense_date >= CAST(:start AS date) AND expense_date < CAST(:end AS date)
        """)["total"])
        profit = _f(sales["profit"])
        summary.update(
            gross_profit=profit,
            margin=profit * 100 / revenue if revenue else 0,
            expenses=expenses,
            net_profit=profit - expenses,
        )

    # ---------------- Inventory (current) ----------------
    inv = one("""
        SELECT COUNT(*) AS product_count,
               COALESCE(SUM(stock * price), 0) AS stock_value
        FROM products WHERE business_id = :bid AND deleted_at IS NULL
    """)

    inventory = {
        "product_count": int(inv["product_count"]),
        "total_units": business.total_products,
        "stock_value": _f(inv["stock_value"]),
        "low_stock": business.low_stock_products,
        "out_of_stock": business.out_of_stock_products,
    }

    # ---------------- Trend ----------------
    if bucket == "hour":
        bucket_sql = f"EXTRACT(HOUR FROM {LOCAL_TS})::int"
    elif bucket == "day":
        bucket_sql = f"({LOCAL_TS})::date"
    else:
        bucket_sql = f"EXTRACT(MONTH FROM {LOCAL_TS})::int"

    trend_rows = {
        r["b"]: r
        for r in rows(f"""
            SELECT {bucket_sql} AS b,
                   SUM(s.total_amount) AS revenue,
                   SUM(s.total_profit) AS profit
            FROM sales s WHERE {IN_RANGE}
            GROUP BY 1
        """)
    }

    expense_rows = {}
    # Expenses only have a date, so there's no hourly breakdown for "today".
    if is_owner and bucket != "hour":
        exp_bucket = "expense_date" if bucket == "day" else "EXTRACT(MONTH FROM expense_date)::int"
        expense_rows = {
            r["b"]: _f(r["total"])
            for r in rows(f"""
                SELECT {exp_bucket} AS b, SUM(amount) AS total FROM expenses
                WHERE business_id = :bid AND deleted_at IS NULL
                  AND expense_date >= CAST(:start AS date) AND expense_date < CAST(:end AS date)
                GROUP BY 1
            """)
        }

    trend = []
    for b, label in _buckets(start, today, now.hour, bucket):
        r = trend_rows.get(b)
        point = {"label": label, "revenue": _f(r["revenue"]) if r else 0}
        if is_owner:
            point["profit"] = _f(r["profit"]) if r else 0
            if bucket != "hour":
                point["expenses"] = expense_rows.get(b, 0)
        trend.append(point)

    # ---------------- Category split ----------------
    # Historical sales keep counting even if the product/category was deleted later.
    category_rows = rows(f"""
        SELECT c.name,
               SUM((si.quantity - si.returned_quantity) * si.selling_price) AS revenue
        FROM sale_items si
        JOIN sales s ON s.id = si.sale_id
        JOIN products p ON p.id = si.product_id
        JOIN categories c ON c.id = p.category_id
        WHERE {IN_RANGE}
        GROUP BY c.name
        HAVING SUM((si.quantity - si.returned_quantity) * si.selling_price) > 0
        ORDER BY revenue DESC
    """)
    categories = [{"name": r["name"], "revenue": _f(r["revenue"])} for r in category_rows[:5]]
    other = sum(_f(r["revenue"]) for r in category_rows[5:])
    if other:
        categories.append({"name": "Other", "revenue": other})

    # ---------------- Top products ----------------
    top_products = [
        {
            "name": r["name"],
            "units": int(r["units"]),
            "revenue": _f(r["revenue"]),
            "profit": _f(r["profit"]) if is_owner else None,
        }
        for r in rows(f"""
            SELECT p.name,
                   SUM(si.quantity - si.returned_quantity) AS units,
                   SUM((si.quantity - si.returned_quantity) * si.selling_price) AS revenue,
                   SUM((si.quantity - si.returned_quantity) * (si.selling_price - si.cost_price)) AS profit
            FROM sale_items si
            JOIN sales s ON s.id = si.sale_id
            JOIN products p ON p.id = si.product_id
            WHERE {IN_RANGE}
            GROUP BY p.id, p.name
            HAVING SUM(si.quantity - si.returned_quantity) > 0
            ORDER BY revenue DESC
            LIMIT 10
        """)
    ]

    # ---------------- Busiest times ----------------
    heatmap = [
        {"dow": int(r["dow"]), "hour": int(r["hour"]), "orders": int(r["orders"])}
        for r in rows(f"""
            SELECT EXTRACT(DOW FROM {LOCAL_TS})::int AS dow,
                   EXTRACT(HOUR FROM {LOCAL_TS})::int AS hour,
                   COUNT(*) AS orders
            FROM sales s WHERE {IN_RANGE}
            GROUP BY 1, 2
        """)
    ]

    # ---------------- Restock suggestions (range-independent) ----------------
    since_30 = datetime.combine(today - timedelta(days=29), datetime.min.time())
    since_60 = datetime.combine(today - timedelta(days=59), datetime.min.time())

    restock = []
    for r in rows(f"""
        WITH velocity AS (
            SELECT si.product_id,
                   SUM(si.quantity - si.returned_quantity) / 30.0 AS daily_rate
            FROM sale_items si JOIN sales s ON s.id = si.sale_id
            WHERE s.business_id = :bid
              AND s.created_at >= (CAST(:since AS timestamp) AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE current_setting('TimeZone'))
            GROUP BY si.product_id
        )
        SELECT p.name, p.stock, p.minimum_stock,
               COALESCE(v.daily_rate, 0) AS daily_rate,
               CASE WHEN v.daily_rate > 0 THEN p.stock / v.daily_rate END AS days_left
        FROM products p
        LEFT JOIN velocity v ON v.product_id = p.id
        WHERE p.business_id = :bid AND p.deleted_at IS NULL
          AND (p.stock < p.minimum_stock OR p.stock = 0
               OR (v.daily_rate > 0 AND p.stock / v.daily_rate < 7))
        ORDER BY days_left ASC NULLS LAST, p.stock ASC
        LIMIT 10
    """, since=since_30):
        restock.append({
            "name": r["name"],
            "stock": r["stock"],
            "minimum_stock": r["minimum_stock"],
            "daily_rate": round(_f(r["daily_rate"]), 2),
            "days_left": round(_f(r["days_left"]), 1) if r["days_left"] is not None else None,
        })

    # ---------------- Dead stock ----------------
    # Products older than 60 days with stock on hand and no sale in 60 days.
    dead_stock = [
        {
            "name": r["name"],
            "stock": r["stock"],
            "value": _f(r["value"]),
            "last_sold": r["last_sold"],
        }
        for r in rows(f"""
            SELECT p.name, p.stock, p.stock * p.price AS value,
                   (MAX(s.created_at) AT TIME ZONE current_setting('TimeZone') AT TIME ZONE 'Asia/Kolkata')::date AS last_sold
            FROM products p
            LEFT JOIN sale_items si ON si.product_id = p.id
            LEFT JOIN sales s ON s.id = si.sale_id
            WHERE p.business_id = :bid AND p.deleted_at IS NULL AND p.stock > 0
              AND p.created_at < (CAST(:since AS timestamp) AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE current_setting('TimeZone'))
            GROUP BY p.id, p.name, p.stock, p.price
            HAVING MAX(s.created_at) IS NULL
                OR MAX(s.created_at) < (CAST(:since AS timestamp) AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE current_setting('TimeZone'))
            ORDER BY value DESC
            LIMIT 10
        """, since=since_60)
    ]

    # ---------------- Inventory value trend ----------------
    # At least 30 days of history so short ranges still draw a line;
    # today's live value is appended since the snapshot runs at 23:55.
    snap_from = min(start.date(), today - timedelta(days=29))
    inventory_trend = [
        {"date": r["snapshot_date"], "stock_value": _f(r["stock_value"]), "total_units": r["total_units"]}
        for r in rows("""
            SELECT snapshot_date, stock_value, total_units
            FROM inventory_snapshots
            WHERE business_id = :bid AND snapshot_date >= :snap_from AND snapshot_date < :today
            ORDER BY snapshot_date
        """, snap_from=snap_from, today=today)
    ]
    inventory_trend.append({
        "date": today,
        "stock_value": inventory["stock_value"],
        "total_units": inventory["total_units"],
    })

    # ---------------- Team ----------------
    team = [
        {"name": r["name"] or "Deleted user", "orders": int(r["orders"]), "revenue": _f(r["revenue"])}
        for r in rows(f"""
            SELECT u.full_name AS name, COUNT(*) AS orders, SUM(s.total_amount) AS revenue
            FROM sales s LEFT JOIN users u ON u.id = s.created_by
            WHERE {IN_RANGE}
            GROUP BY s.created_by, u.full_name
            ORDER BY revenue DESC
            LIMIT 10
        """)
    ]

    # ---------------- Top customers ----------------
    top_customers = [
        {"contact": mask_contact(r["customer_contact"]), "orders": int(r["orders"]), "revenue": _f(r["revenue"])}
        for r in rows(f"""
            SELECT s.customer_contact, COUNT(*) AS orders, SUM(s.total_amount) AS revenue
            FROM sales s WHERE {IN_RANGE}
            GROUP BY s.customer_contact
            ORDER BY revenue DESC
            LIMIT 5
        """)
    ]

    return DashboardResponse(
        range=range_,
        is_owner=is_owner,
        summary=summary,
        inventory=inventory,
        trend=trend,
        categories=categories,
        top_products=top_products,
        heatmap=heatmap,
        restock=restock,
        dead_stock=dead_stock,
        inventory_trend=inventory_trend,
        team=team,
        top_customers=top_customers,
    )
