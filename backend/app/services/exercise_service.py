from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.exercise_model import Exercise
from app.schemas.exercise_schema import ExerciseCreate, ExerciseUpdate, ExerciseRead


def create_exercise(
        db: Session,
        exercise_in: ExerciseCreate
) -> Exercise:

    exercise = Exercise(**exercise_in.model_dump())

    db.add(exercise)

    try:
        db.commit()
        db.refresh(exercise)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An exercise with this name already exists.",
        )

    return exercise


def list_exercises(
    db: Session,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0
) -> list[Exercise]:
    query = db.query(Exercise)

    if search:
        query = query.filter(Exercise.name.ilike(f"%{search}%"))

    return (
        query
        .order_by(Exercise.name)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_exercise(
        db: Session,
        exercise_id: int
) -> Exercise:

    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )

    return exercise


def update_exercise(
    db: Session,
    exercise_id: int,
    exercise_in: ExerciseUpdate
) -> Exercise:

    exercise = get_exercise(db, exercise_id)

    update_data = exercise_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(exercise, field, value)

    try:
        db.commit()
        db.refresh(exercise)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exercise could not be updated because it conflicts with existing data.",
        )

    return exercise


def delete_exercise(
        db: Session,
        exercise_id: int
) -> None:

    exercise = get_exercise(db, exercise_id)

    db.delete(exercise)
    db.commit()