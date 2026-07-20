from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.program_schema import ProgramRead, ProgramCreate, ProgramUpdate
from app.services.program_service import create_program, delete_program, update_program, list_programs, get_program

router = APIRouter(
    prefix="/programs",
    tags=["programs"]
)

@router.post("/", response_model=ProgramRead, status_code=status.HTTP_201_CREATED)
def create_program_route(
        program_in: ProgramCreate,
        db: Session = Depends(get_db),
):
    return create_program(db, program_in)


@router.get("/", response_model=list[ProgramRead])
def list_programs_route(
        user_id: int | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
        db: Session = Depends(get_db),
):
    return list_programs(db, user_id, search, limit, offset)


@router.get("/{program_id}", response_model=ProgramRead)
def get_program_route(
        program_id: int,
        db: Session = Depends(get_db),
):
    return get_program(db, program_id)


@router.patch("/{program_id}", response_model=ProgramRead)
def update_program_route(
        program_id: int,
        program_in: ProgramUpdate,
        db: Session = Depends(get_db),
):
    return update_program(db, program_id, program_in)

@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program_route(
        program_id: int,
        db: Session = Depends(get_db),
):
    delete_program(db, program_id)
    return None

