import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, text
from sqlalchemy.orm import Session

from models import (
    Business,
    BusinessMember,
    Category,
    Expense,
    InventorySnapshot,
    Job,
    Product,
    Sale,
    SaleItem,
    User,
)
from models.enums import MemberRole, SubscriptionPlan, SubscriptionStatus
from services.dashboard_service import invalidate_dashboard
from utils.inventory import apply_stock_change
from utils.password import hash_password, verify_password


IST = ZoneInfo("Asia/Kolkata")
DAYS = 100

# category -> (custom fields, [(product, cost price, minimum stock, dynamic fields)])
CATALOG = {
    "Electronics": (
        [("brand", "text"), ("warranty_months", "number")],
        [
            ("USB-C Cable", 120, 15, {"brand": "boAt", "warranty_months": 6}),
            ("Wireless Mouse", 450, 8, {"brand": "Logitech", "warranty_months": 12}),
            ("Bluetooth Earbuds", 1200, 5, {"brand": "boAt", "warranty_months": 12}),
            ("Power Bank 10000mAh", 900, 6, {"brand": "Mi", "warranty_months": 6}),
            ("Phone Charger 20W", 350, 10, {"brand": "Ambrane", "warranty_months": 6}),
        ],
    ),
    "Groceries": (
        [("weight_grams", "number"), ("expiry_date", "date")],
        [
            ("Basmati Rice 1kg", 95, 25, {"weight_grams": 1000, "expiry_date": "2027-06-30"}),
            ("Toor Dal 1kg", 140, 20, {"weight_grams": 1000, "expiry_date": "2027-03-31"}),
            ("Sunflower Oil 1L", 150, 15, {"weight_grams": 910, "expiry_date": "2027-01-31"}),
            ("Tea Powder 250g", 110, 12, {"weight_grams": 250, "expiry_date": "2027-08-31"}),
            ("Sugar 1kg", 45, 30, {"weight_grams": 1000, "expiry_date": "2027-12-31"}),
        ],
    ),
    "Stationery": (
        [("brand", "text")],
        [
            ("A4 Notebook", 40, 30, {"brand": "Classmate"}),
            ("Ball Pen Pack", 50, 25, {"brand": "Reynolds"}),
            ("Geometry Box", 120, 10, {"brand": "Camlin"}),
            ("Highlighter Set", 90, 10, {"brand": "Faber-Castell"}),
        ],
    ),
    "Personal Care": (
        [("brand", "text"), ("expiry_date", "date")],
        [
            ("Shampoo 180ml", 110, 12, {"brand": "Clinic Plus", "expiry_date": "2027-05-31"}),
            ("Toothpaste 150g", 85, 20, {"brand": "Colgate", "expiry_date": "2027-09-30"}),
            ("Bath Soap Pack", 120, 15, {"brand": "Dove", "expiry_date": "2027-10-31"}),
            ("Face Wash 100ml", 140, 10, {"brand": "Himalaya", "expiry_date": "2027-04-30"}),
        ],
    ),
}

MONTHLY_EXPENSES = [("Shop Rent", 15000, 15000), ("Electricity Bill", 2000, 3500), ("Staff Salary", 12000, 12000)]
DAILY_EXPENSES = [("Tea & Snacks", 50, 300), ("Transport", 100, 500), ("Packaging Material", 200, 800)]


def _ist_to_db(db: Session):
    # Timestamp columns are naive in the DB server's TimeZone (server_default now()),
    # and the dashboard converts them to IST, so write them the same way.
    db_tz = ZoneInfo(db.execute(text("SELECT current_setting('TimeZone')")).scalar())
    return lambda dt: dt.replace(tzinfo=IST).astimezone(db_tz).replace(tzinfo=None)


def seed_business(
    db: Session,
    email: str,
    password: str,
    business_name: str,
    start_date: date,
):
    if db.query(User.id).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    rng = random.Random()
    to_db = _ist_to_db(db)
    start_ts = to_db(datetime.combine(start_date, time(9)))

    try:
        user = User(
            id=uuid4(),
            full_name=email.split("@")[0].title(),
            email=email,
            password_hash=hash_password(password),
            has_completed_onboarding=True,
            created_at=start_ts,
        )
        # LIFETIME so the seeded account never gets subscription-blocked.
        business = Business(
            id=uuid4(),
            owner_id=user.id,
            name=business_name,
            subscription_plan=SubscriptionPlan.LIFETIME,
            subscription_status=SubscriptionStatus.ACTIVE,
            subscription_start=start_ts,
            total_products=0,
            low_stock_products=0,
            out_of_stock_products=0,
            created_at=start_ts,
        )
        db.add_all([
            user,
            business,
            BusinessMember(business_id=business.id, user_id=user.id, role=MemberRole.OWNER),
        ])

        products = []
        for cat_name, (fields, items) in CATALOG.items():
            category = Category(
                id=uuid4(),
                business_id=business.id,
                name=cat_name,
                fields=[
                    {"id": str(uuid4()), "key": key, "type": ftype, "order": i, "required": False, "meta": {}}
                    for i, (key, ftype) in enumerate(fields, start=1)
                ],
                created_at=start_ts,
            )
            db.add(category)

            for name, cost, min_stock, dyn in items:
                product = Product(
                    id=uuid4(),
                    business_id=business.id,
                    category_id=category.id,
                    name=name,
                    price=Decimal(cost),
                    stock=0,
                    minimum_stock=min_stock,
                    dynamic_fields=dyn,
                    created_at=start_ts,
                )
                apply_stock_change(
                    business=business,
                    product=product,
                    quantity_delta=rng.randint(min_stock * 3, min_stock * 6),
                    is_new=True,
                )
                db.add(product)
                products.append(product)

        db.add_all([
            Job(business_id=business.id, created_by=user.id, title="Sales Assistant",
                location="Main Store", salary="₹12,000 / month", email=email, contact="9876543210"),
            Job(business_id=business.id, created_by=user.id, title="Delivery Boy",
                location="Main Store", salary="₹9,000 / month", contact="9123456780"),
        ])

        customers = [str(rng.randint(6_000_000_000, 9_999_999_999)) for _ in range(40)]
        sales, sale_items, expenses, snapshots = [], [], [], []

        for d in range(DAYS):
            day = start_date + timedelta(days=d)

            # Restock some low/out products so the stock alerts come and go.
            for p in products:
                if p.stock < p.minimum_stock and rng.random() < 0.3:
                    apply_stock_change(
                        business=business,
                        product=p,
                        quantity_delta=rng.randint(p.minimum_stock * 2, p.minimum_stock * 5),
                    )

            n_sales = rng.randint(3, 12) + (5 if day.weekday() >= 5 else 0)
            for _ in range(n_sales):
                in_stock = [p for p in products if p.stock > 0]
                if not in_stock:
                    break

                sale_id = uuid4()
                ts = to_db(datetime.combine(day, time(rng.randint(9, 20), rng.randint(0, 59))))
                total = profit = Decimal("0.00")

                for p in rng.sample(in_stock, min(len(in_stock), rng.randint(1, 3))):
                    qty = rng.randint(1, min(p.stock, 4))
                    cost = Decimal(p.price)
                    sell = (cost * Decimal(str(round(rng.uniform(1.1, 1.5), 2)))).quantize(Decimal("1"))
                    returned = 1 if rng.random() < 0.03 else 0  # occasional return

                    apply_stock_change(business=business, product=p, quantity_delta=returned - qty)

                    # Same math as sale_service: profit_loss is for the full qty,
                    # sale totals only count the non-returned qty.
                    sale_items.append({
                        "id": uuid4(), "sale_id": sale_id, "product_id": p.id,
                        "quantity": qty, "returned_quantity": returned,
                        "is_fully_returned": returned == qty,
                        "selling_price": sell, "cost_price": cost,
                        "profit_loss": (sell - cost) * qty, "created_at": ts,
                    })
                    total += sell * (qty - returned)
                    profit += (sell - cost) * (qty - returned)

                sales.append({
                    "id": sale_id, "business_id": business.id, "created_by": user.id,
                    "customer_contact": rng.choice(customers),
                    "total_amount": total, "total_profit": profit, "created_at": ts,
                })

            if d == 0 or day.day == 1:
                for title, lo, hi in MONTHLY_EXPENSES:
                    expenses.append(_expense(business.id, title, rng.randint(lo, hi), day, True, start_ts))
            for title, lo, hi in DAILY_EXPENSES:
                if rng.random() < 0.4:
                    expenses.append(_expense(business.id, title, rng.randint(lo, hi), day, False, start_ts))

            snapshots.append({
                "id": uuid4(), "business_id": business.id, "snapshot_date": day,
                "total_units": sum(p.stock for p in products),
                "stock_value": sum(p.stock * p.price for p in products),
                "low_stock": business.low_stock_products,
                "out_of_stock": business.out_of_stock_products,
            })

        # ORM flush for the setup rows (audited as CREATE); the bulk history goes
        # through Core inserts, which skip the audit listener like the snapshot job.
        db.flush()
        db.execute(insert(Sale), sales)
        db.execute(insert(SaleItem), sale_items)
        db.execute(insert(Expense), expenses)
        db.execute(insert(InventorySnapshot), snapshots)
        db.commit()

    except Exception:
        db.rollback()
        raise

    invalidate_dashboard(business.id)

    return {
        "message": "Mock data created",
        "email": email,
        "business_id": str(business.id),
        "from": start_date,
        "to": start_date + timedelta(days=DAYS - 1),
        "products": len(products),
        "sales": len(sales),
        "sale_items": len(sale_items),
        "expenses": len(expenses),
        "snapshots": len(snapshots),
    }


def delete_seeded_business(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    business_ids = [b.id for b in user.owned_businesses]

    # Core delete: the DB cascades users -> businesses -> every business-scoped
    # table, without loading thousands of rows through the ORM.
    try:
        db.execute(delete(User).where(User.id == user.id))
        db.commit()
    except Exception:
        db.rollback()
        raise

    for business_id in business_ids:
        invalidate_dashboard(business_id)

    return {"message": "Seeded user and business deleted", "email": email}


def _expense(business_id, title, amount, day, recurring, created_at):
    return {
        "id": uuid4(), "business_id": business_id, "title": title,
        "amount": Decimal(amount), "expense_date": day,
        "is_recurring": recurring, "created_at": created_at,
    }
