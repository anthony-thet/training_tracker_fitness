from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.exercise_schema import ExerciseRead, ExerciseCreate, ExerciseUpdate
from app.services.exercise_service import create_exercise, delete_exercise, update_exercise, list_exercises, get_exercise

router = APIRouter(
    prefix="/exercises",
    tags=["exercises"],
)

@router.post("/", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def create_exercise_route(
    exercise_in: ExerciseCreate,
    db: Session = Depends(get_db),
):
    return create_exercise(db, exercise_in)


@router.get("/", response_model=list[ExerciseRead])
def list_exercises_route(
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return list_exercises(
        db,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise_route(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    return get_exercise(db, exercise_id)


@router.patch("/{exercise_id}", response_model=ExerciseRead)
def update_exercise_route(
    exercise_id: int,
    exercise_in: ExerciseUpdate,
    db: Session = Depends(get_db),
):
    return update_exercise(db, exercise_id, exercise_in)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_route(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    delete_exercise(db, exercise_id)