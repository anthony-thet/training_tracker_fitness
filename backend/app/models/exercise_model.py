from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    primary_muscle: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    equipment: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )