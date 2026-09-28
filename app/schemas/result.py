"""Result schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.result import NormalizationMethod


class NormalizationRunCreate(BaseModel):
    rubric_id: int
    method: NormalizationMethod
    parameters: Optional[dict] = None


class NormalizationRunResponse(BaseModel):
    id: int
    event_id: int
    rubric_id: int
    method: NormalizationMethod
    parameters: Optional[str]
    initiated_by: int
    completed_at: Optional[datetime]
    is_published: bool
    published_at: Optional[datetime]
    warnings: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ResultResponse(BaseModel):
    id: int
    run_id: int
    project_id: int
    raw_aggregate: Optional[float]
    normalized_score: Optional[float]
    rank: Optional[int]
    tie_rank: Optional[int]
    review_count: int
    criterion_count: int
    project_title: Optional[str] = None
    team_name: Optional[str] = None

    class Config:
        from_attributes = True


class RunWithResultsResponse(NormalizationRunResponse):
    results: List[ResultResponse] = []
