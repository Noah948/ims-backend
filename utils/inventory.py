from utils.stock import stock_state

def apply_stock_change(
    *,
    business,
    product,
    quantity_delta: int = 0,
    new_minimum_stock: int | None = None,
    is_new: bool = False,
    is_delete: bool = False,
):
    old_state = stock_state(product.stock, product.minimum_stock)

    if is_delete:
        business.total_products -= product.stock
        if old_state == "low" and business.low_stock_products > 0:
            business.low_stock_products -= 1
        elif old_state == "out" and business.out_of_stock_products > 0:
            business.out_of_stock_products -= 1
        return

    if quantity_delta != 0:
        product.stock += quantity_delta
        business.total_products += quantity_delta

    if new_minimum_stock is not None:
        product.minimum_stock = new_minimum_stock

    new_state = stock_state(product.stock, product.minimum_stock)

    if is_new:
        if new_state == "low":
            business.low_stock_products += 1
        elif new_state == "out":
            business.out_of_stock_products += 1
        return

    if old_state != new_state:
        if old_state == "low" and business.low_stock_products > 0:
            business.low_stock_products -= 1
        elif old_state == "out" and business.out_of_stock_products > 0:
            business.out_of_stock_products -= 1
        if new_state == "low":
            business.low_stock_products += 1
        elif new_state == "out":
            business.out_of_stock_products += 1