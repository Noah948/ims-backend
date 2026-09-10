from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4, UUID
from datetime import datetime
from fastapi import HTTPException, status

from models.job import Job
from models.business import Business
from schema.job import JobCreate, JobUpdate


def create_job(
    db: Session,
    business_id: UUID,
    user_id: UUID,
    data: JobCreate,
):
    business = db.get(Business, business_id)

    if not business.location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please update your business location before posting a job",
        )

    job = Job(
        id=uuid4(),
        business_id=business_id,
        created_by=user_id,
        title=data.title,
        location=data.location or business.location,
        salary=data.salary,
        email=data.email,
        contact=data.contact,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_jobs(
    db: Session,
    business_id: UUID,
):
    stmt = select(Job).where(
        Job.business_id == business_id
    )

    return db.execute(stmt).scalars().all()


def get_job(
    db: Session,
    business_id: UUID,
    job_id: UUID,
):
    stmt = (
        select(Job)
        .where(Job.id == job_id)
        .where(Job.business_id == business_id)
    )

    job = db.execute(stmt).scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


def update_job(
    db: Session,
    business_id: UUID,
    job_id: UUID,
    data: JobUpdate,
):
    job = get_job(db, business_id, job_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    job.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(job)

    return job


def delete_job(
    db: Session,
    business_id: UUID,
    job_id: UUID,
):
    job = get_job(db, business_id, job_id)

    db.delete(job)
    db.commit()

    return job


def get_public_jobs(
    db: Session,
    limit: int = 10,
):
    stmt = (
        select(Job)
        .order_by(Job.created_at.desc())
        .limit(limit)
    )

    return db.execute(stmt).scalars().all()