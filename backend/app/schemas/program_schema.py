from datetime import datetime

from pydantic import BaseModel

class ProgramBase(BaseModel):
    name: str
    description: str | None = None

class ProgramCreate(ProgramBase):
    user_id: int

class ProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class ProgramRead(ProgramBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
