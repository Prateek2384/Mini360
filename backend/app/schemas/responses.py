import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class QuestionRead(ORMModel):
    id: uuid.UUID
    category: str
    text: str
    position: int


class AnswerIn(BaseModel):
    question_id: uuid.UUID
    score: int = Field(ge=1, le=5)


class ResponseSubmit(BaseModel):
    answers: list[AnswerIn] = Field(min_length=1, max_length=50)


class SubmitResult(BaseModel):
    response_id: uuid.UUID
    submitted_at: datetime
