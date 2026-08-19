from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import WorkoutDay, ProgramWeek, Program
from app.schemas.workout_day_schema import WorkoutDayCreate, WorkoutDayUpdate
from app.services.program_week_service import get_program_week


def create_workout_day(
        db: Session,
        week_id: int,
        workout_day_in: WorkoutDayCreate,
        user_id: int,
) -> WorkoutDay:

    program_week = get_program_week(db, week_id, user_id)

    workout_day = WorkoutDay(
        program_week_id=program_week.id,
        **workout_day_in.model_dump(),
    )

    db.add(workout_day)

    try:
        db.commit()
        db.refresh(workout_day)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Workout day with this day order already exists for this program week.",
        )

    return workout_day


def list_workout_days(
        db: Session,
        week_id: int,
        user_id: int,
) -> list[WorkoutDay]:

    get_program_week(db, week_id, user_id)

    workout_days = (
        db.query(WorkoutDay)
        .filter(WorkoutDay.program_week_id == week_id)
        .order_by(WorkoutDay.day_order)
        .all()
    )

    return workout_days


def get_workout_day(
        db: Session,
        day_id: int,
        user_id: int,
) -> WorkoutDay:

    workout_day = (
        db.query(WorkoutDay)
        .join(ProgramWeek, WorkoutDay.program_week_id == ProgramWeek.id)
        .join(Program, ProgramWeek.program_id == Program.id)
        .filter(
            WorkoutDay.id == day_id,
            Program.user_id == user_id,
        )
        .first()
    )

    if workout_day is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout day not found",
        )

    return workout_day


def update_workout_day(
        db: Session,
        day_id: int,
        workout_day_in: WorkoutDayUpdate,
        user_id: int,
) -> WorkoutDay:

    workout_day = get_workout_day(db, day_id, user_id)

    update_data = workout_day_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(workout_day, field, value)

    db.commit()
    db.refresh(workout_day)

    return workout_day


def delete_workout_day(
        db: Session,
        day_id: int,
        user_id: int,
) -> None:

    workout_day = get_workout_day(db, day_id, user_id)

    db.delete(workout_day)
    db.commit()