from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.job import JobCreate, JobUpdate, JobResponse

from services.job_service import (
    create_job,
    get_jobs,
    get_job,
    update_job,
    delete_job,
    get_public_jobs
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ---------------- PUBLIC JOB LIST (NO AUTH) ----------------
@router.get(
    "/",
    response_model=List[JobResponse]
)
def list_public_jobs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return get_public_jobs(db=db, limit=limit)


# ---------------- CREATE ----------------
@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job_endpoint(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_job(db=db, user_id=current_user.id, data=data)


# ---------------- READ ALL (USER - PRIVATE) ----------------
@router.get(
    "/my",
    response_model=List[JobResponse]
)
def list_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_jobs(db=db, user_id=current_user.id)


# ---------------- READ SINGLE ----------------
@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def retrieve_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = get_job(db, user_id=current_user.id, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------- UPDATE ----------------
@router.put(
    "/{job_id}",
    response_model=JobResponse
)
@router.patch(
    "/{job_id}",
    response_model=JobResponse
)
def update_job_endpoint(
    job_id: UUID,
    data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = update_job(
        db=db,
        user_id=current_user.id,
        job_id=job_id,
        data=data
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------- DELETE ----------------
@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_job_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = delete_job(db=db, user_id=current_user.id, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return