from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.planned_set_schema import PlannedSetCreate, PlannedSetUpdate, PlannedSetRead
from app.services.planned_set_service import create_planned_set, list_planned_sets, get_planned_set, update_planned_set, delete_planned_set


router = APIRouter(
    tags=["planned sets"],
)


@router.post("/workout-exercises/{workout_exercise_id}/sets", response_model=PlannedSetRead, status_code=status.HTTP_201_CREATED)
def create_planned_set_route(
    workout_exercise_id: int,
    planned_set_in: PlannedSetCreate,
    db: Session = Depends(get_db),
):
    return create_planned_set(db, workout_exercise_id, planned_set_in)


@router.get("/workout-exercises/{workout_exercise_id}/sets", response_model=list[PlannedSetRead])
def list_planned_sets_route(
    workout_exercise_id: int,
    db: Session = Depends(get_db),
):
    return list_planned_sets(db, workout_exercise_id)


@router.get("/planned-sets/{set_id}", response_model=PlannedSetRead)
def get_planned_set_route(
    set_id: int,
    db: Session = Depends(get_db),
):
    return get_planned_set(db, set_id)


@router.patch("/planned-sets/{set_id}", response_model=PlannedSetRead)
def update_planned_set_route(
    set_id: int,
    planned_set_in: PlannedSetUpdate,
    db: Session = Depends(get_db),
):
    return update_planned_set(db, set_id, planned_set_in)


@router.delete("/planned-sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planned_set_route(
    set_id: int,
    db: Session = Depends(get_db),
):
    delete_planned_set(db, set_id)