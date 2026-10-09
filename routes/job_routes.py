from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, get_current_business

from models.user_model import User
from models.business import Business

from schema.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
)

from services.job_service import (
    create_job,
    get_jobs,
    get_job,
    update_job,
    delete_job,
    get_public_jobs,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get(
    "/",
    response_model=List[JobResponse],
)
def list_public_jobs(
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return get_public_jobs(
        db,
        limit,
    )


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job_endpoint(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
):
    return create_job(
        db,
        business.id,
        current_user.id,
        data,
    )


@router.get(
    "/my",
    response_model=List[JobResponse],
)
def list_my_jobs(
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_jobs(
        db,
        business.id,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def retrieve_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return get_job(
        db,
        business.id,
        job_id,
    )


@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
@router.patch(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job_endpoint(
    job_id: UUID,
    data: JobUpdate,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    return update_job(
        db,
        business.id,
        job_id,
        data,
    )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db),
    business: Business = Depends(get_current_business),
):
    delete_job(
        db,
        business.id,
        job_id,
    )

    return None