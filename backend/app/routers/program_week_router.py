from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.program_week_schema import ProgramWeekRead, ProgramWeekCreate, ProgramWeekUpdate
from app.services.program_week_service import create_program_week, delete_program_week, update_program_week, list_program_weeks, get_program_week


router = APIRouter(
    tags=["programs weeks"]
)


@router.post("/programs/{program_id}/weeks", response_model=ProgramWeekRead, status_code=status.HTTP_201_CREATED)
def create_program_week_route(
        program_id: int,
        program_week_in: ProgramWeekCreate,
        db: Session = Depends(get_db),
):
    return create_program_week(db, program_id, program_week_in)


@router.get("/programs/{program_id}/weeks", response_model=List[ProgramWeekRead])
def list_program_weeks_route(
        program_id: int,
        db: Session = Depends(get_db),
):
    return list_program_weeks(db, program_id)


@router.get("/program_week/{week_id}", response_model=ProgramWeekRead)
def get_program_week_route(
        week_id: int,
        db: Session = Depends(get_db),
):
    return get_program_week(db, week_id)


@router.patch("/program_week/{week_id}", response_model=ProgramWeekUpdate)
def update_program_week_route(
        week_id: int,
        program_week_in: ProgramWeekUpdate,
        db: Session = Depends(get_db),
):
    return update_program_week(db, week_id, program_week_in)


@router.delete("/program_week/{week_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program_week_route(
        week_id: int,
        db: Session = Depends(get_db),
):
    delete_program_week(db, week_id)