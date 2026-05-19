from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user

from schema.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,

    CategoryFieldCreate,
    CategoryFieldUpdate,
    CategoryFieldResponse,

    # ✅ NEW
    CategoryFieldReorder
)

from services.category_service import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category,

    add_category_field,
    update_category_field,
    delete_category_field,
    reorder_category_fields
)

from models.user_model import User

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# =====================================================
# CATEGORY ROUTES
# =====================================================

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return create_category(
        db=db,
        user_id=str(current_user.id),
        data=data
    )


@router.get(
    "/",
    response_model=List[CategoryResponse]
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_categories(
        db=db,
        user_id=str(current_user.id)
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def retrieve_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = get_category(
        db=db,
        user_id=str(current_user.id),
        category_id=str(category_id)
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category_endpoint(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    category = update_category(
        db=db,
        user_id=str(current_user.id),
        category_id=str(category_id),
        data=data
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category_endpoint(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    deleted = delete_category(
        db=db,
        user_id=str(current_user.id),
        category_id=str(category_id)
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return


# =====================================================
# FIELD ROUTES
# =====================================================

# ---------------- ADD FIELD ----------------
@router.post(
    "/{category_id}/fields",
    response_model=CategoryFieldResponse,
    status_code=status.HTTP_201_CREATED
)
def add_field_endpoint(
    category_id: UUID,
    data: CategoryFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        field = add_category_field(
            db=db,
            user_id=str(current_user.id),
            category_id=str(category_id),
            data=data
        )

        if not field:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return field

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# ---------------- REORDER FIELDS ----------------
@router.patch(
    "/{category_id}/fields/reorder",
    response_model=List[CategoryFieldResponse]
)
def reorder_fields_endpoint(
    category_id: UUID,
    payload: CategoryFieldReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        fields = reorder_category_fields(
            db=db,
            user_id=str(current_user.id),
            category_id=str(category_id),
            ordered_field_ids=payload.ordered_field_ids
        )

        if fields is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        return fields

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    
# ---------------- UPDATE FIELD ----------------
@router.patch(
    "/{category_id}/fields/{field_id}",
    response_model=CategoryFieldResponse
)
def update_field_endpoint(
    category_id: UUID,
    field_id: UUID,
    data: CategoryFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        field = update_category_field(
            db=db,
            user_id=str(current_user.id),
            category_id=str(category_id),
            field_id=str(field_id),
            data=data
        )

        if not field:
            raise HTTPException(
                status_code=404,
                detail="Field or category not found"
            )

        return field

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------- DELETE FIELD ----------------
@router.delete(
    "/{category_id}/fields/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_field_endpoint(
    category_id: UUID,
    field_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    deleted = delete_category_field(
        db=db,
        user_id=str(current_user.id),
        category_id=str(category_id),
        field_id=str(field_id)
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Field or category not found"
        )

    return



