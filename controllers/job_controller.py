from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from services.job_service import (
    create_job as create_job_service,
    get_jobs as get_jobs_service,
    get_job as get_job_service,
    update_job as update_job_service,
    delete_job as delete_job_service,
    get_public_jobs as get_public_jobs_service,
)
from schema.job import JobCreate, JobUpdate


def create_job(db: Session, business_id: UUID, user_id: UUID, data: JobCreate):
    return create_job_service(db, business_id, user_id, data)


def get_jobs(db: Session, business_id: UUID):
    return get_jobs_service(db, business_id)


def get_job(db: Session, business_id: UUID, job_id: UUID):
    job = get_job_service(db, business_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def update_job(db: Session, business_id: UUID, job_id: UUID, data: JobUpdate):
    job = update_job_service(db, business_id, job_id, data)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def delete_job(db: Session, business_id: UUID, job_id: UUID):
    job = delete_job_service(db, business_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return None


def get_public_jobs(db: Session, limit: int):
    return get_public_jobs_service(db, limit)