from pydantic import BaseModel

class ExerciseBase(BaseModel):
    name: str
    category: str | None = None
    primary_muscle: str | None = None
    equipment: str | None = None
    description: str | None = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    primary_muscle: str | None = None
    equipment: str | None = None
    description: str | None = None

class ExerciseRead(ExerciseBase):
    id: int

    model_config = {
        "from_attributes": True
    }