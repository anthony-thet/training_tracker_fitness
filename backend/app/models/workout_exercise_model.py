from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    workout_day_id: Mapped[int] = mapped_column(
        ForeignKey("workout_days.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"),
        nullable=False,
        index=True,
    )

    exercise_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    workout_day = relationship(
        "WorkoutDay",
        back_populates="workout_exercises",
    )

    exercise = relationship("Exercise")

    planned_sets: Mapped[list["PlannedSet"]] = relationship(
        "PlannedSet",
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
    )