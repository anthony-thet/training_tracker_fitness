from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    program_week_id: Mapped[int] = mapped_column(
        ForeignKey("program_weeks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    day_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    program_week: Mapped["ProgramWeek"] = relationship(
        "ProgramWeek",
        back_populates="workout_days",
    )

    workout_exercises: Mapped[list["WorkoutExercise"]] = relationship(
        "WorkoutExercise",
        back_populates="workout_day",
        cascade="all, delete-orphan",
    )