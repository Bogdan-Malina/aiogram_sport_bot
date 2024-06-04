from typing import List

from sqlalchemy import ForeignKey, DateTime, BigInteger
from sqlalchemy import String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[int] = mapped_column(nullable=False, default=0)
    code: Mapped["Code"] = relationship(back_populates="user", cascade="all, delete-orphan")
    workout_plans: Mapped[List["WorkoutPlan"]] = relationship(cascade="all, delete-orphan")


class Code(Base):
    __tablename__ = "codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(255), unique=True)
    user_id: Mapped[BigInteger] = mapped_column(
        ForeignKey("users.telegram_id"),
        nullable=True,
        default=None
    )
    user: Mapped["User"] = relationship(back_populates="code")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class FreeWorkoutPlan(Base):
    __tablename__ = "free_workout_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
