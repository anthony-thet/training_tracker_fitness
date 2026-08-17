from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.models import User
from app.schemas.workout_exercise_schema import WorkoutExerciseCreate, WorkoutExerciseUpdate, WorkoutExerciseRead
from app.services.workout_exercise_service import create_workout_exercise, list_workout_exercises, get_workout_exercise, update_workout_exercise, delete_workout_exercise


router = APIRouter(
    tags=["workout exercises"],
)


@router.post("/workout-days/{day_id}/exercises", response_model=WorkoutExerciseRead, status_code=status.HTTP_201_CREATED)
def create_workout_exercise_route(
    day_id: int,
    workout_exercise_in: WorkoutExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_workout_exercise(db, day_id, workout_exercise_in, current_user.id)


@router.get("/workout-days/{day_id}/exercises", response_model=list[WorkoutExerciseRead])
def list_workout_exercises_route(
    day_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_workout_exercises(db, day_id, current_user.id)


@router.get("/workout-exercises/{workout_exercise_id}", response_model=WorkoutExerciseRead)
def get_workout_exercise_route(
    workout_exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_workout_exercise(db, workout_exercise_id, current_user.id)


@router.patch("/workout-exercises/{workout_exercise_id}",
    response_model=WorkoutExerciseRead)
def update_workout_exercise_route(
    workout_exercise_id: int,
    workout_exercise_in: WorkoutExerciseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_workout_exercise(db, workout_exercise_id, workout_exercise_in, current_user.id)


@router.delete("/workout-exercises/{workout_exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_exercise_route(
    workout_exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_workout_exercise(db, workout_exercise_id, current_user.id)