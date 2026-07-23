from pydantic import BaseModel


class ProgramWeekBase(BaseModel):
    week_number: int
    notes: str | None = None

class ProgramWeekCreate(ProgramWeekBase):
    pass

class ProgramWeekUpdate(BaseModel):
    week_number: int | None = None
    notes: str | None = None

class ProgramWeekRead(ProgramWeekBase):
    id: int
    program_id: int

    model_config = {
        "from_attributes": True
    }