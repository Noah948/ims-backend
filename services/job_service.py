from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4, UUID
from datetime import datetime
from fastapi import HTTPException

from models.job import Job
from models.user_model import User
from schema.job import JobCreate, JobUpdate


# ---------------- CREATE ----------------
def create_job(db: Session, user_id: UUID, data: JobCreate):
    user = db.get(User, user_id)

    if not user.location:
        raise HTTPException(
            status_code=400,
            detail="Please update your profile location before posting a job"
        )

    job = Job(
        id=uuid4(),
        user_id=user_id,
        business_name=data.business_name,
        title=data.title,

        # ❌ description removed

        location=data.location or user.location,
        salary=data.salary,
        email=data.email,
        contact=data.contact,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# ---------------- READ ALL (USER) ----------------
def get_jobs(db: Session, user_id: UUID):
    stmt = select(Job).where(Job.user_id == user_id)
    return db.execute(stmt).scalars().all()


# ---------------- READ SINGLE ----------------
def get_job(db: Session, user_id: UUID, job_id: UUID):
    stmt = (
        select(Job)
        .where(Job.id == job_id)
        .where(Job.user_id == user_id)
    )
    return db.execute(stmt).scalar_one_or_none()


# ---------------- UPDATE ----------------
def update_job(db: Session, user_id: UUID, job_id: UUID, data: JobUpdate):
    job = get_job(db, user_id, job_id)
    if not job:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job


# ---------------- DELETE ----------------
def delete_job(db: Session, user_id: UUID, job_id: UUID):
    job = get_job(db, user_id, job_id)
    if not job:
        return None

    db.delete(job)
    db.commit()
    return job


# ---------------- PUBLIC JOBS (HOMEPAGE) ----------------
def get_public_jobs(db: Session, limit: int = 10):
    stmt = (
        select(Job)
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()