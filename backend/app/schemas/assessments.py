import uuid
from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field


class AssessmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    closes_at: AwareDatetime | None = None


class AssessmentLaunch(BaseModel):
    closes_at: AwareDatetime | None = None


class AssessmentRead(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    min_responses: int
    closes_at: datetime | None
    closed_at: datetime | None
    self_completed_at: datetime | None
    created_at: datetime
    rater_response_count: int


class AssessmentStatus(BaseModel):
    id: uuid.UUID
    status: str
    closes_at: datetime | None
    closed_at: datetime | None
    min_responses: int
    invitation_count: int
    rater_response_count: int
    self_completed: bool
    results_unlocked: bool
