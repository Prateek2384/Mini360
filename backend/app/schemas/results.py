import uuid

from pydantic import BaseModel


class ScoreTriple(BaseModel):
    self_score: float | None
    others_mean: float
    gap: float | None


class CategoryResult(ScoreTriple):
    category: str


class ItemResult(ScoreTriple):
    question_id: uuid.UUID
    position: int
    category: str
    text: str


class ResultsResponse(BaseModel):
    assessment_id: uuid.UUID
    title: str
    rater_response_count: int
    overall: ScoreTriple
    categories: list[CategoryResult]
    items: list[ItemResult]
    focus_areas: list[ItemResult]
    focus_note: str
