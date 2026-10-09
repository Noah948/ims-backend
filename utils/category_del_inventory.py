from sqlalchemy import func, case
from models.product import Product


def get_category_stock_impact(db, category_id, business_id):
    totals = db.query(
        func.coalesce(func.sum(Product.stock), 0),
        func.count(case((Product.stock == 0, 1))),
        func.count(
            case((
                (Product.stock > 0) &
                (Product.stock <= Product.minimum_stock),
                1
            ))
        )
    ).filter(
        Product.category_id == category_id,
        Product.business_id == business_id
    ).first()
    return totals