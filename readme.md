# Commands

venv\Scripts\activate


# TODO

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