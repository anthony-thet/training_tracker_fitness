from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PlannedSet(Base):
    __tablename__ = "planned_sets"

    __table_args__ = (
        UniqueConstraint("workout_exercise_id", "set_order", name="uq_planned_set_order"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    set_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    target_reps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    target_weight: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    target_rpe: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    workout_exercise: Mapped["WorkoutExercise"] = relationship(
        "WorkoutExercise",
        back_populates="planned_sets",
    )