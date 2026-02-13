from sqlalchemy import func, case
from models.product import Product


def get_category_stock_impact(db, category_id, user_id):
    """
    Returns:
        total_stock, out_count, low_count
    """

    totals = db.query(
        func.coalesce(func.sum(Product.stock), 0),

        func.count(
            case((Product.stock == 0, 1))
        ),

        func.count(
            case((
                (Product.stock > 0) &
                (Product.stock <= Product.minimum_stock),
                1
            ))
        )

    ).filter(
        Product.category_id == category_id,
        Product.user_id == user_id
    ).first()

    return totals
