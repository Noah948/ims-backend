Here’s the **exact sequence** to implement multi-product sales:

---

### 🔹 STEP 1 — Create new model

* Create `Sale` (main transaction)
* Keep fields: `id`, `user_id`, `contact`, `total_amount`, `total_profit`, `created_at`

---

### 🔹 STEP 2 — Convert current model

* Rename current `Sale` → `SaleItem`
* Add `sale_id` (FK → Sale)
* Add `cost_price` field
* Keep: `quantity`, `selling_price`, `profit_loss`

---

### 🔹 STEP 3 — Relationships

* `Sale` → `sale_items` (one-to-many)
* `SaleItem` → `sale` (many-to-one)
* Keep product + user relationships

---

### 🔹 STEP 4 — Update schemas

* Change `SaleCreate`:

  * remove `product_id`, `quantity`, `selling_price`
  * add `items: List[...]`

* Create `SaleItemCreate` schema:

  * `product_id`
  * `quantity`
  * `selling_price`

---

### 🔹 STEP 5 — Update API request format

* Accept:

```json
{
  "contact": "9876543210",
  "items": [...]
}
```

---

### 🔹 STEP 6 — Refactor service: create_sale

* Start DB transaction
* Create empty `Sale`
* Loop through items:

  * lock product
  * check stock
  * reduce stock
  * calculate profit
  * create `SaleItem`
* Accumulate totals
* Update Sale totals
* Commit

---

### 🔹 STEP 7 — Update delete logic

* Fetch all `SaleItem`s
* Restore stock for each
* Delete items + sale

---

### 🔹 STEP 8 — Update response schema

* `SaleResponse`:

  * include list of items
  * include totals

---

### 🔹 STEP 9 — Migration

* Generate migration
* Apply changes to DB

---

### 🔹 STEP 10 — Test in Swagger

* Create sale with multiple items
* Delete sale → stock should restore correctly
