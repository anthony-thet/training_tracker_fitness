from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import ProgramWeek, Program
from app.schemas.program_week_schema import ProgramWeekCreate, ProgramWeekUpdate
from app.services.program_service import get_program


def create_program_week(
        db: Session,
        program_id: int,
        program_week_in: ProgramWeekCreate,
        user_id: int,
) -> ProgramWeek:

    program = get_program(db, program_id, user_id)

    program_week = ProgramWeek(
        program_id=program.id,
        **program_week_in.model_dump()
    )

    db.add(program_week)
    db.commit()
    db.refresh(program_week)

    return program_week


def list_program_weeks(
        db: Session,
        program_id: int,
        user_id: int,
) -> list[ProgramWeek]:

    get_program(db, program_id, user_id)

    program_weeks = (
        db.query(ProgramWeek)
        .filter(ProgramWeek.program_id == program_id)
        .order_by(ProgramWeek.week_number)
        .all()
    )

    return program_weeks


def get_program_week(
        db: Session,
        week_id: int,
        user_id: int,
) -> ProgramWeek:

    program_week = (
        db.query(ProgramWeek)
        .join(Program, ProgramWeek.program_id == Program.id)
        .filter(
            ProgramWeek.id == week_id,
            Program.user_id == user_id,
        )
        .first()
    )

    if program_week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program week not found",
        )

    return program_week


def update_program_week(
        db: Session,
        week_id: int,
        program_week_in: ProgramWeekUpdate,
        user_id: int,
) -> ProgramWeek:

    program_week = get_program_week(db, week_id, user_id)

    update_data = program_week_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(program_week, field, value)

    db.commit()
    db.refresh(program_week)

    return program_week


def delete_program_week(
        db: Session,
        week_id: int,
        user_id: int,
) -> None:

    program_week = get_program_week(db, week_id, user_id)

    db.delete(program_week)
    db.commit()


