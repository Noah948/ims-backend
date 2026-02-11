from utils.stock import stock_state
def apply_stock_change(
    *,
    user,
    product,
    quantity_delta: int = 0,
    new_minimum_stock: int | None = None,
    is_new: bool = False,
    is_delete: bool = False,   # 🔥 NEW FLAG
):
    old_state = stock_state(product.stock, product.minimum_stock)

    # ---------------- DELETE PRODUCT ----------------
    if is_delete:
        # remove stock from total
        user.total_products -= product.stock

        # remove state contribution safely
        if old_state == "low" and user.low_stock_count > 0:
            user.low_stock_count -= 1

        elif old_state == "out" and user.out_of_stock_count > 0:
            user.out_of_stock_count -= 1

        return

    # ---------------- APPLY STOCK CHANGE ----------------
    if quantity_delta != 0:
        product.stock += quantity_delta
        user.total_products += quantity_delta

    # ---------------- APPLY MINIMUM STOCK CHANGE ----------------
    if new_minimum_stock is not None:
        product.minimum_stock = new_minimum_stock

    new_state = stock_state(product.stock, product.minimum_stock)

    # ---------------- NEW PRODUCT REGISTRATION ----------------
    if is_new:
        if new_state == "low":
            user.low_stock_count += 1
        elif new_state == "out":
            user.out_of_stock_count += 1
        return

    # ---------------- NORMAL STATE TRANSITION ----------------
    if old_state != new_state:

        if old_state == "low" and user.low_stock_count > 0:
            user.low_stock_count -= 1

        elif old_state == "out" and user.out_of_stock_count > 0:
            user.out_of_stock_count -= 1

        if new_state == "low":
            user.low_stock_count += 1

        elif new_state == "out":
            user.out_of_stock_count += 1
