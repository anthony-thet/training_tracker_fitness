from datetime import datetime

from pydantic import BaseModel


class PlannedSetDetailRead(BaseModel):
    id: int
    workout_exercise_id: int
    set_order: int
    target_reps: int
    target_weight: float | None = None
    target_rpe: float | None = None
    notes: str | None = None

    model_config = {
        "from_attributes": True
    }


class ExerciseDetailRead(BaseModel):
    id: int
    name: str
    category: str | None = None
    primary_muscle: str | None = None
    equipment: str | None = None
    description: str | None = None

    model_config = {
        "from_attributes": True
    }


class WorkoutExerciseDetailRead(BaseModel):
    id: int
    workout_day_id: int
    exercise_id: int
    exercise_order: int
    notes: str | None = None

    exercise: ExerciseDetailRead
    planned_sets: list[PlannedSetDetailRead] = []

    model_config = {
        "from_attributes": True
    }


class WorkoutDayDetailRead(BaseModel):
    id: int
    program_week_id: int
    name: str
    day_order: int
    notes: str | None = None
    created_at: datetime

    workout_exercises: list[WorkoutExerciseDetailRead] = []

    model_config = {
        "from_attributes": True
    }


class ProgramWeekDetailRead(BaseModel):
    id: int
    program_id: int
    week_number: int
    notes: str | None = None

    workout_days: list[WorkoutDayDetailRead] = []

    model_config = {
        "from_attributes": True
    }


class ProgramDetailRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    program_weeks: list[ProgramWeekDetailRead] = []

    model_config = {
        "from_attributes": True
    }