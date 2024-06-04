from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    telegram_id: int
    name: str
    code: str


@dataclass
class WorkoutPlan:
    description: str
    user_id: int
    date: datetime.date


@dataclass
class FreeWorkoutPlan:
    description: str
    date: datetime.date
