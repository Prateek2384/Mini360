import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel

GoalStatus = Literal["not_started", "in_progress", "done"]


class GoalIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    due_date: date
    status: GoalStatus = "not_started"


class GoalsUpdate(BaseModel):
    goals: list[GoalIn] = Field(min_length=1, max_length=2)


class GoalRead(ORMModel):
    id: uuid.UUID
    title: str
    description: str | None
    due_date: date
    status: str
    created_at: datetime
