from pydantic import BaseModel


class PlannedSetBase(BaseModel):
    set_order: int
    target_reps: int
    target_weight: float | None = None
    target_rpe: float | None = None
    notes: str | None = None


class PlannedSetCreate(PlannedSetBase):
    pass


class PlannedSetUpdate(BaseModel):
    set_order: int | None = None
    target_reps: int | None = None
    target_weight: float | None = None
    target_rpe: float | None = None
    notes: str | None = None


class PlannedSetRead(PlannedSetBase):
    id: int
    workout_exercise_id: int

    model_config = {
        "from_attributes": True
    }