from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.program_model import Program
from app.models.user_model import User
from app.schemas.program_schema import ProgramCreate, ProgramUpdate


def create_program(
        db: Session,
        program_in: ProgramCreate
) -> Program:

    user = (
        db.query(User)
        .filter(User.id == program_in.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    program = Program(**program_in.model_dump())

    db.add(program)

    try:
        db.commit()
        db.refresh(program)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program could not be created",
        )

    return program


def list_programs(
    db: Session,
    user_id: int | None = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Program]:

    programs = db.query(Program)


    if user_id is not None:
        programs = programs.filter(Program.user_id == user_id)

    if search:
        programs = programs.filter(Program.name.ilike(f"%{search}%"))

    programs = (
        programs
        .order_by(Program.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return programs


def get_program(
        db: Session,
        program_id: int
) -> Program:

    program = (
        db.query(Program)
        .filter(Program.id == program_id)
        .first()
    )

    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )

    return program


def update_program(
        db: Session,
        program_id: int,
        program_in: ProgramUpdate
) -> Program:

    program = get_program(db, program_id)

    update_data = program_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(program, field, value)

    try:
        db.commit()
        db.refresh(program)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Program could not be updated because it conflicts with existing data.",
        )

    return program


def delete_program(
        db: Session,
        program_id: int
) -> None:

    program = get_program(db, program_id)

    db.delete(program)
    db.commit()