import math
from sqlalchemy import select, func
from sqlalchemy.orm import Session


def paginate(query, db: Session, page: int = 1, limit: int = 10):
    """
    Reusable offset-based pagination utility.
    """

    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    offset = (page - 1) * limit

    # Total count
    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    )

    # Paginated items
    items = db.scalars(
        query.offset(offset).limit(limit)
    ).all()

    total_pages = math.ceil(total / limit) if total else 1

    return {
        "data": items,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }