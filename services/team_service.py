from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Optional

from models.team import Team
from schema.team import TeamCreate, TeamUpdate


# ---------------- CREATE ----------------
def create_team(db: Session, user_id: UUID, data: TeamCreate) -> Team:
    now = datetime.utcnow()

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
        created_at=now,
        updated_at=now
    )

    db.add(team)
    db.commit()
    db.refresh(team)
    return team


# ---------------- READ ALL ----------------
def get_teams(db: Session, user_id: UUID) -> List[Team]:
    stmt = (
        select(Team)
        .where(Team.user_id == user_id)
        .order_by(Team.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


# ---------------- READ SINGLE ----------------
def get_team(db: Session, user_id: UUID, team_id: UUID) -> Optional[Team]:
    stmt = (
        select(Team)
        .where(Team.id == team_id)
        .where(Team.user_id == user_id)
    )
    return db.execute(stmt).scalar_one_or_none()


# ---------------- UPDATE ----------------
def update_team(
    db: Session,
    user_id: UUID,
    team_id: UUID,
    data: TeamUpdate
) -> Optional[Team]:

    team = get_team(db, user_id, team_id)
    if not team:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)

    team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(team)
    return team


# ---------------- DELETE (HARD DELETE) ----------------
def delete_team(db: Session, user_id: UUID, team_id: UUID) -> Optional[Team]:
    team = get_team(db, user_id, team_id)
    if not team:
        return None

    db.delete(team)
    db.commit()
    return team
