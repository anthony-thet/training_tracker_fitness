from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import PlannedSet
from app.schemas.planned_set_schema import PlannedSetCreate, PlannedSetUpdate
from app.services.workout_exercise_service import get_workout_exercise


def create_planned_set(
    db: Session,
    workout_exercise_id: int,
    planned_set_in: PlannedSetCreate,
) -> PlannedSet:

    workout_exercise = get_workout_exercise(db, workout_exercise_id)

    planned_set = PlannedSet(
        workout_exercise_id=workout_exercise.id,
        **planned_set_in.model_dump(),
    )

    db.add(planned_set)
    db.commit()
    db.refresh(planned_set)

    return planned_set


def list_planned_sets(
    db: Session,
    workout_exercise_id: int,
) -> list[PlannedSet]:

    get_workout_exercise(db, workout_exercise_id)

    planned_sets = (
        db.query(PlannedSet)
        .filter(PlannedSet.workout_exercise_id == workout_exercise_id)
        .order_by(PlannedSet.set_order)
        .all()
    )

    return planned_sets


def get_planned_set(
    db: Session,
    set_id: int,
) -> PlannedSet:

    planned_set = (
        db.query(PlannedSet)
        .filter(PlannedSet.id == set_id)
        .first()
    )

    if planned_set is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planned set not found",
        )

    return planned_set


def update_planned_set(
    db: Session,
    set_id: int,
    planned_set_in: PlannedSetUpdate,
) -> PlannedSet:

    planned_set = get_planned_set(db, set_id)

    update_data = planned_set_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(planned_set, field, value)

    db.commit()
    db.refresh(planned_set)

    return planned_set


def delete_planned_set(
    db: Session,
    set_id: int,
) -> None:

    planned_set = get_planned_set(db, set_id)

    db.delete(planned_set)
    db.commit()