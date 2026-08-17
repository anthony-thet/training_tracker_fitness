from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependencies import get_current_user
from app.models import User
from app.schemas.program_detail_schema import ProgramDetailRead
from app.schemas.program_schema import ProgramRead, ProgramCreate, ProgramUpdate
from app.services.program_service import create_program, delete_program, update_program, list_programs, get_program, \
    get_program_detail

router = APIRouter(
    prefix="/programs",
    tags=["programs"]
)

@router.post("/", response_model=ProgramRead, status_code=status.HTTP_201_CREATED)
def create_program_route(
        program_in: ProgramCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return create_program(db, program_in, current_user.id)


@router.get("/", response_model=list[ProgramRead])
def list_programs_route(
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return list_programs(db, current_user.id, search, limit, offset)


@router.get("/{program_id}/detail", response_model=ProgramDetailRead)
def get_program_detail_route(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_program_detail(db, program_id, current_user.id)


@router.get("/{program_id}", response_model=ProgramRead)
def get_program_route(
        program_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return get_program(db, program_id, current_user.id)


@router.patch("/{program_id}", response_model=ProgramRead)
def update_program_route(
        program_id: int,
        program_in: ProgramUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    return update_program(db, program_id, program_in, current_user.id)

@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program_route(
        program_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    delete_program(db, program_id, current_user.id)