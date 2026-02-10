from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4
from datetime import datetime

from models.team import Team
from schema.team import TeamCreate, TeamUpdate


# ---------------- CREATE ----------------
def create_team(db: Session, user_id: str, data: TeamCreate):
    team = Team(
        id=uuid4(),
        user_id=user_id,
        name=data.name,
        role=data.role,
        gender=data.gender,
        email=data.email,
        contact=data.contact,
        emergency_contact=data.emergency_contact,
        address=data.address,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


# ---------------- READ ALL ----------------
def get_teams(db: Session, user_id: str):
    stmt = select(Team).where(Team.user_id == user_id)
    return db.execute(stmt).scalars().all()


# ---------------- READ SINGLE ----------------
def get_team(db: Session, user_id: str, team_id: str):
    stmt = (
        select(Team)
        .where(Team.id == team_id)
        .where(Team.user_id == user_id)
    )
    return db.execute(stmt).scalar_one_or_none()


# ---------------- UPDATE ----------------
def update_team(db: Session, user_id: str, team_id: str, data: TeamUpdate):
    team = get_team(db, user_id, team_id)
    if not team:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)

    team.updated_at = datetime.utcnow()  # type: ignore
    db.commit()
    db.refresh(team)
    return team


# ---------------- DELETE (HARD DELETE) ----------------
def delete_team(db: Session, user_id: str, team_id: str):
    team = get_team(db, user_id, team_id)
    if not team:
        return None

    db.delete(team)
    db.commit()
    return team
