from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.models import User
from app.schemas.program_week_schema import ProgramWeekRead, ProgramWeekCreate, ProgramWeekUpdate
from app.services.program_week_service import create_program_week, delete_program_week, update_program_week, list_program_weeks, get_program_week


router = APIRouter(
    tags=["programs weeks"]
)


@router.post("/programs/{program_id}/weeks", response_model=ProgramWeekRead, status_code=status.HTTP_201_CREATED)
def create_program_week_route(
        program_id: int,
        program_week_in: ProgramWeekCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return create_program_week(db, program_id, program_week_in, current_user.id)


@router.get("/programs/{program_id}/weeks", response_model=list[ProgramWeekRead])
def list_program_weeks_route(
        program_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return list_program_weeks(db, program_id, current_user.id)


@router.get("/program-weeks/{week_id}", response_model=ProgramWeekRead)
def get_program_week_route(
        week_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return get_program_week(db, week_id, current_user.id)


@router.patch("/program-weeks/{week_id}", response_model=ProgramWeekRead)
def update_program_week_route(
        week_id: int,
        program_week_in: ProgramWeekUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return update_program_week(db, week_id, program_week_in, current_user.id)


@router.delete("/program-weeks/{week_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program_week_route(
        week_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    delete_program_week(db, week_id, current_user.id)