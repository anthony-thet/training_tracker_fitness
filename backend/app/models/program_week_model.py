from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProgramWeek(Base):
    __tablename__ = "program_weeks"

    __table_args__ = (
        UniqueConstraint("program_id", "week_number", name="uq_program_week_number"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    week_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    program = relationship(
        "Program",
        back_populates="program_weeks",
    )

    workout_days = relationship(
        "WorkoutDay",
        back_populates="program_week",
        cascade="all, delete-orphan",
    )