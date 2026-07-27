from datetime import datetime

from pydantic import BaseModel


class WorkoutDayBase(BaseModel):
    name: str
    day_order: int
    notes: str | None = None


class WorkoutDayCreate(WorkoutDayBase):
    pass


class WorkoutDayUpdate(BaseModel):
    name: str | None = None
    day_order: int | None = None
    notes: str | None = None


class WorkoutDayRead(WorkoutDayBase):
    id: int
    program_week_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }