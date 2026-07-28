from pydantic import BaseModel


class WorkoutExerciseBase(BaseModel):
    exercise_id: int
    exercise_order: int
    notes: str | None = None


class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass


class WorkoutExerciseUpdate(BaseModel):
    exercise_id: int | None = None
    exercise_order: int | None = None
    notes: str | None = None


class WorkoutExerciseRead(WorkoutExerciseBase):
    id: int
    workout_day_id: int

    model_config = {
        "from_attributes": True
    }