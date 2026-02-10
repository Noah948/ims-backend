from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user
from models.user_model import User
from schema.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse
)
from services.team_service import (
    create_team,
    get_teams,
    get_team,
    update_team,
    delete_team
)

router = APIRouter(prefix="/teams", tags=["Teams"])


# ---------------- CREATE ----------------
@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED
)
def create_team_endpoint(
    data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_team(db=db, user_id=str(current_user.id), data=data)


# ---------------- READ ALL ----------------
@router.get(
    "/",
    response_model=List[TeamResponse]
)
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_teams(db=db, user_id=str(current_user.id))


# ---------------- READ SINGLE ----------------
@router.get(
    "/{team_id}",
    response_model=TeamResponse
)
def retrieve_team(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team = get_team(db=db, user_id=str(current_user.id), team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team member not found")
    return team


# ---------------- UPDATE ----------------
@router.put(
    "/{team_id}",
    response_model=TeamResponse
)
@router.patch(
    "/{team_id}",
    response_model=TeamResponse
)
def update_team_endpoint(
    team_id: str,
    data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team = update_team(
        db=db,
        user_id=str(current_user.id),
        team_id=team_id,
        data=data
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team member not found")
    return team


# ---------------- DELETE ----------------
@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_team_endpoint(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team = delete_team(db=db, user_id=str(current_user.id), team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team member not found")
    return
