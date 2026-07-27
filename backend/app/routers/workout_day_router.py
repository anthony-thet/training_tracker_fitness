from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.workout_day_schema import WorkoutDayCreate, WorkoutDayUpdate, WorkoutDayRead
from app.services.workout_day_service import create_workout_day, delete_workout_day, update_workout_day, list_workout_days, get_workout_day


router = APIRouter(
    tags=["workout days"],
)


@router.post("/program-weeks/{week_id}/days", response_model=WorkoutDayRead, status_code=status.HTTP_201_CREATED)
def create_workout_day_route(
        week_id: int,
        workout_day_in: WorkoutDayCreate,
        db: Session = Depends(get_db),
):
    return create_workout_day(db, week_id, workout_day_in)


@router.get("/program-weeks/{week_id}/days", response_model=list[WorkoutDayRead])
def list_workout_days_route(
        week_id: int,
        db: Session = Depends(get_db),
):
    return list_workout_days(db, week_id)


@router.get("/workout-days/{day_id}", response_model=WorkoutDayRead)
def get_workout_day_route(
        day_id: int,
        db: Session = Depends(get_db),
):
    return get_workout_day(db, day_id)


@router.patch("/workout-days/{day_id}", response_model=WorkoutDayRead)
def update_workout_day_route(
        day_id: int,
        workout_day_in: WorkoutDayUpdate,
        db: Session = Depends(get_db),
):
    return update_workout_day(db, day_id, workout_day_in)


@router.delete("/workout-days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_day_route(
        day_id: int,
        db: Session = Depends(get_db),
):
    delete_workout_day(db, day_id)