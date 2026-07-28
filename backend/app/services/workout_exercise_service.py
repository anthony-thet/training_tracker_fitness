from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import WorkoutExercise
from app.schemas.workout_exercise_schema import WorkoutExerciseCreate, WorkoutExerciseUpdate
from app.services.workout_day_service import get_workout_day
from app.services.exercise_service import get_exercise


def create_workout_exercise(
    db: Session,
    day_id: int,
    workout_exercise_in: WorkoutExerciseCreate,
) -> WorkoutExercise:

    workout_day = get_workout_day(db, day_id)

    exercise = get_exercise(db, workout_exercise_in.exercise_id)

    workout_exercise = WorkoutExercise(
        workout_day_id=workout_day.id,
        exercise_id=exercise.id,
        exercise_order=workout_exercise_in.exercise_order,
        notes=workout_exercise_in.notes,
    )

    db.add(workout_exercise)
    db.commit()
    db.refresh(workout_exercise)

    return workout_exercise


def list_workout_exercises(
    db: Session,
    day_id: int,
) -> list[WorkoutExercise]:

    get_workout_day(db, day_id)

    workout_exercises = (
        db.query(WorkoutExercise)
        .filter(WorkoutExercise.workout_day_id == day_id)
        .order_by(WorkoutExercise.exercise_order)
        .all()
    )

    return workout_exercises


def get_workout_exercise(
    db: Session,
    workout_exercise_id: int,
) -> WorkoutExercise:

    workout_exercise = (
        db.query(WorkoutExercise)
        .filter(WorkoutExercise.id == workout_exercise_id)
        .first()
    )

    if workout_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout exercise not found",
        )

    return workout_exercise


def update_workout_exercise(
    db: Session,
    workout_exercise_id: int,
    workout_exercise_in: WorkoutExerciseUpdate,
) -> WorkoutExercise:

    workout_exercise = get_workout_exercise(db, workout_exercise_id)

    update_data = workout_exercise_in.model_dump(exclude_unset=True)

    if "exercise_id" in update_data:
        exercise = get_exercise(db, update_data["exercise_id"])
        update_data["exercise_id"] = exercise.id

    for field, value in update_data.items():
        setattr(workout_exercise, field, value)

    db.commit()
    db.refresh(workout_exercise)

    return workout_exercise


def delete_workout_exercise(
    db: Session,
    workout_exercise_id: int,
) -> None:

    workout_exercise = get_workout_exercise(db, workout_exercise_id)

    db.delete(workout_exercise)
    db.commit()