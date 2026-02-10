def stock_state(stock: int, minimum_stock: int) -> str:
    if stock == 0:
        return "out"
    elif stock < minimum_stock:
        return "low"
    return "normal"
