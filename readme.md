# TODO

## 1️⃣ Missing: Proper Relationships (ORM Side)

Right now you're using ForeignKeys but not defining relationships everywhere.

For example:

* `User` should have:

  * products
  * sales
  * teams
  * categories
  * payments

This makes querying MUCH cleaner:

Instead of:

```python
db.query(Product).filter(Product.user_id == user.id)
```

You could:

```python
user.products
```

That’s more professional ORM usage.

---

## 2️⃣ Sale Table Issue ⚠️ (Important)

Your `Sale` table only stores:

```python
product_id
quantity
selling_price
profit_loss
```

But think professionally:

If product is deleted or its price changes, what happens?

👉 A good system stores:

* product_name (snapshot)
* cost_price (at time of sale)
* selling_price (at time of sale)
* category_name (optional snapshot)

Because sales are historical records.

Professionally, Sale should not depend too much on Product.

---

## 4️⃣ No Audit Logs (Very Professional Feature)

Add:

### 🧾 ActivityLog Table

Store:

* user_id
* action_type (created_product, deleted_category, etc.)
* reference_id
* timestamp

For real SaaS this is powerful.

---

## 5️⃣ Soft Delete Consistency

You soft delete Product.
But Category is hard delete with cascade.

This can create issues.

Professional SaaS usually:

* Soft deletes everything
* Or archives instead of deleting

You might want:

```
deleted_at column in Category
```

Instead of actual delete.

---

## 2️⃣ Expense Tracking

Inventory is not only sale.
Add:

* Expense table
* Rent, electricity, salary etc.

Then you can calculate:

```
Net Profit = Sales - Expenses
```

---

## 4️⃣ Role-Based Access Control (VERY SaaS-Level)

Right now Team has `role` as text.

Better:
Define:

* owner
* manager
* staff
* accountant

And restrict routes based on role.

---

## 5️⃣ Reports Export

Add:

* CSV export
* PDF export
* Monthly reports

Clients love reports.

---

## 6️⃣ Low Stock Alerts

Since you already track:

* low_stock_count
* out_of_stock_count

You can:

* Send email
* Send notification
* Show alert badge

---

### 🔹 Use UUID default generation everywhere consistently

Some tables generate in DB, some in Python.

Choose ONE pattern.

---

### 🔹 Add Indexes

For example:

* user_id should always be indexed
* product_id in Sale should be indexed
* category_id in Product should be indexed

Performance matters in SaaS.

---

### 🔹 Add NOT NULL where required

Example:
Some tables don’t enforce nullable properly.

---

### 🔹 Use Enums Instead of Text

Instead of:

```
status = Column(Text)
```

Use PostgreSQL ENUM for:

* Payment status
* Role
* Field type

More professional.

---

# 🎯 If I Were You (Next Step Recommendation)

Since you like doing things modular and production-ready:

Next logical feature to build:

> **Purchase + StockMovement system**

That will upgrade your IMS from:
“CRUD Inventory App”
to
“Professional Inventory System”